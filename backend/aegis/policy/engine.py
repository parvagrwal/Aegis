import json
import os
from pathlib import Path

class PolicyEngine:
    def __init__(self):
        self.config = {}
        self._load()
        
    def _load(self):
        p = Path(__file__).parent.parent.parent / "config" / "policy.v1.json"
        if p.exists():
            with open(p, "r") as f:
                self.config = json.load(f)
                
    def _temperature(self):
        """Fitted calibration temperature. 1.0 (identity) unless a real fit
        has been written by backend/aegis/policy/calibration.py."""
        cal = self.config.get("calibration", {})
        if cal.get("status") == "fitted":
            try:
                t = float(cal.get("temperature", 1.0))
                if t > 0:
                    return t
            except (TypeError, ValueError):
                pass
        return 1.0

    def assess(self, features: list) -> dict:
        prior = self.config.get("prior_logit_milli", -500)

        score = prior
        fired_features = []
        for feat in features:
            fid = feat.get("id") if isinstance(feat, dict) else getattr(feat, "id", None)
            weight = feat.get("weight") if isinstance(feat, dict) else getattr(feat, "weight", 0)
            score += weight
            fired_features.append(fid)

        # Calibration: the fitted temperature rescales the raw additive
        # score before banding. score stays raw for auditability.
        temperature = self._temperature()
        calibrated_score = score / temperature

        bands = self.config.get("bands", {}).get("risk", {})
        risk = "LOW"
        if calibrated_score >= bands.get("CRITICAL", 8500):
            risk = "CRITICAL"
        elif calibrated_score >= bands.get("HIGH", 5000):
            risk = "HIGH"
        elif calibrated_score >= bands.get("ELEVATED", 2000):
            risk = "ELEVATED"

        return {
            "score": score,
            "calibrated_score": calibrated_score,
            "temperature": temperature,
            "risk": risk,
            "features": fired_features
        }

engine = PolicyEngine()

def assess_case(features: list) -> dict:
    return engine.assess(features)
