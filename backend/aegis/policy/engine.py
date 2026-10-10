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

        # Family caps (anti-double-counting): correlated signals within a family
        # don't stack linearly.
        #
        # INTEL cap = 2500 = weight of intel.label_malicious, the strongest
        # single intel signal. Rationale: a known attacker must be able to
        # reach HIGH on intel alone (this was the pre-family-scoring behavior:
        # 2500 - 500 prior = 2000 = HIGH band). Capping INTEL at 2000 would
        # make single-family INTEL max out at 1500 (ELEVATED) after the -500
        # prior, demoting known attackers to "uncertain" -- a regression, not
        # a design choice. label_malicious (2500) + infra (1500) = 4000 still
        # caps at 2500, so double-counting within intel is prevented.
        FAMILY_CAPS = {"INTEL": 2500, "CODE": 2000, "BEHAVIORAL": 2000}
        score = prior
        families_contributing = 0
        for fam, fam_score in family_scores.items():
            if fam_score > 0:
                score += min(fam_score, FAMILY_CAPS[fam])
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
            
        # Conviction rule.
        # INTEL is curated ground truth (human-verified attacker list), not a
        # noisy signal. A saturated INTEL family (known attacker, at the 2500
        # cap) is sufficient for HIGH on its own -- this restores the
        # pre-family-scoring behavior.
        # CODE and BEHAVIORAL signals are noisy; their caps + prior max out at
        # ELEVATED (2000 - 500 = 1500), so they inherently require corroboration
        # and can never reach HIGH alone.
        # CRITICAL always requires 2+ families as a safety invariant (it is
        # mathematically unreachable with a single family: max 2500 - 500).
        if risk == "CRITICAL" and families_contributing < 2:
            risk = "HIGH"
        if risk == "HIGH" and families_contributing < 2:
            intel_saturated = family_scores["INTEL"] >= FAMILY_CAPS["INTEL"]
            if not intel_saturated:
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
