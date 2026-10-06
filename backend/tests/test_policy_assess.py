from aegis.models.case import Feature
from aegis.policy.engine import assess_case

def test_policy_assess():
    # Empty
    res = assess_case([])
    assert res["score"] == -500
    assert res["risk"] == "LOW"
    
    # Mild
    res = assess_case([Feature(id="sim.approval_unlimited_to_eoa", weight=2500, data={})])
    assert res["score"] == -500 + 2500 # 2000
    assert res["risk"] == "ELEVATED"
    
    # High
    res = assess_case([
        Feature(id="sim.approval_unlimited_to_eoa", weight=2500, data={}),
        Feature(id="code.sweeper_pattern", weight=3000, data={})
    ])
    assert res["score"] == 5000
    assert res["risk"] == "HIGH"
    
    # Critical
    res = assess_case([
        Feature(id="sim.approval_unlimited_to_eoa", weight=2500, data={}),
        Feature(id="code.sweeper_pattern", weight=3000, data={}),
        Feature(id="intel.label_malicious", weight=4000, data={})
    ])
    assert res["score"] == 9000
    assert res["risk"] == "CRITICAL"
