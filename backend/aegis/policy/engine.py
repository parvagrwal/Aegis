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

        # Family mapping
        families = {
            "INTEL": ["intel.label_malicious", "infra.shared_attacker_infrastructure"],
            "CODE": ["code.unverified", "code.sweeper_pattern"],
            "BEHAVIORAL": ["sim.approval_unlimited_to_eoa", "sim.approval_to_eoa_limited", 
                           "sim.subject_outflow_no_inflow", "sim.large_value_transfer", 
                           "sim.price_unavailable"]
        }
        
        feat_to_family = {}
        for fam, fids in families.items():
            for fid in fids:
                feat_to_family[fid] = fam
                
        family_scores = {"INTEL": 0, "CODE": 0, "BEHAVIORAL": 0}

        fired_features = []
        for feat in features:
            fid = feat.get("id") if isinstance(feat, dict) else getattr(feat, "id", None)
            weight = feat.get("weight") if isinstance(feat, dict) else getattr(feat, "weight", 0)
            
            # Aggregate into family
            fam = feat_to_family.get(fid, "BEHAVIORAL") # default to behavioral if unknown
            family_scores[fam] += weight
            fired_features.append(fid)

        # Cap families at 2000
        score = prior
        families_contributing = 0
        for fam, fam_score in family_scores.items():
            if fam_score > 0:
                score += min(fam_score, 2000)
                families_contributing += 1

        # Calibration
        temperature = self._temperature()
        calibrated_score = score / temperature

        bands = self.config.get("bands", {}).get("risk", {})
        
        # Determine raw risk
        risk = "LOW"
        if calibrated_score >= bands.get("CRITICAL", 8500):
            risk = "CRITICAL"
        elif calibrated_score >= bands.get("HIGH", 5000):
            risk = "HIGH"
        elif calibrated_score >= bands.get("ELEVATED", 2000):
            risk = "ELEVATED"
            
        # Two-family rule
        if risk in ("HIGH", "CRITICAL") and families_contributing < 2:
            risk = "ELEVATED"

        return {
            "score": score,
            "calibrated_score": calibrated_score,
            "temperature": temperature,
            "risk": risk,
            "features": fired_features,
            "family_scores": family_scores
        }

engine = PolicyEngine()

def assess_case(features: list) -> dict:
    return engine.assess(features)
