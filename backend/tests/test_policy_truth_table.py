import json
import itertools
from pathlib import Path
from aegis.policy.rules import decide

def test_truth_table():
    contexts = ["POST_CONFIRMATION_PROTECTED", "PRE_EXECUTION", "FIREHOSE"]
    risks = ["CRITICAL", "HIGH", "ELEVATED", "LOW"]
    confs = ["HIGH", "MEDIUM", "LOW"]
    sufficients = [True, False]
    # 3 * 4 * 3 * 2 * X = 432 => X = 6
    effects = ["APPROVAL", "TRANSFER", "DELEGATION", "MINT", "BURN", "NONE"]
    
    expected_r99_path = Path(__file__).parent / "expected_r99.json"
    if not expected_r99_path.exists():
        with open(expected_r99_path, "w") as f:
            json.dump([], f)
            
    with open(expected_r99_path, "r") as f:
        expected_r99 = set(tuple(x) for x in json.load(f))
        
    r99_hits = set()
    total = 0
    
    for c, r, cf, s, e in itertools.product(contexts, risks, confs, sufficients, effects):
        total += 1
        rule = decide(c, r, cf, s, e)
        assert rule is not None
        if rule == "R99":
            r99_hits.add((c, r, cf, s, e))
            
    assert total == 432
    assert r99_hits == expected_r99
