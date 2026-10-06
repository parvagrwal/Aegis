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
                
    def assess(self, features: list) -> dict:
        prior = self.config.get("prior_logit_milli", -500)
        
        score = prior
        fired_features = []
        for feat in features:
            fid = feat.get("id") if isinstance(feat, dict) else getattr(feat, "id", None)
            weight = feat.get("weight") if isinstance(feat, dict) else getattr(feat, "weight", 0)
            score += weight
            fired_features.append(fid)
            
        bands = self.config.get("bands", {}).get("risk", {})
        risk = "LOW"
        if score >= bands.get("CRITICAL", 8500):
            risk = "CRITICAL"
        elif score >= bands.get("HIGH", 5000):
            risk = "HIGH"
        elif score >= bands.get("ELEVATED", 2000):
            risk = "ELEVATED"
            
        return {
            "score": score,
            "risk": risk,
            "features": fired_features
        }

engine = PolicyEngine()

def assess_case(features: list) -> dict:
    return engine.assess(features)
