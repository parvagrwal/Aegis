import asyncio
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from aegis.models.case import CaseContext
from aegis.chain.simulate import SimResult
from aegis.chain.decoder import decode_tx
from aegis.chain.effects import effects_from_logs, net_flows
from aegis.detect.roles import determine_roles
from aegis.detect.features import extract_features
from aegis.detect.triage import triage
from aegis.policy.engine import assess_case

def load_cases(path):
    with open(path, "r") as f:
        return json.load(f)

async def evaluate_case(case):
    # Mock pipeline for harness
    tx = {"from": "0x1", "to": "0x2", "input": "0x", "type": "0x2"}
    decoded = decode_tx(tx)
    sim = SimResult(path="C", status="success", logs=[], effects_source="abi_semantics")
    effects = effects_from_logs(sim.logs)
    flows = net_flows(effects)
    subject, init = determine_roles(tx, decoded, effects, [])
    
    ctx = CaseContext(
        case_id=case["case_id"],
        tx=tx,
        decoded=decoded,
        sim=sim,
        effects=effects,
        sig_effects=[],
        net_flows=flows,
        subject=subject or "0x1",
        initiator=init or "0x1",
        profiles={},
        labels={}
    )
    
    feats = extract_features(ctx)
    res = assess_case(feats)
    
    # Verdict derivation
    verdict = "malicious" if res["risk"] in ("HIGH", "CRITICAL") else "benign"
    
    return {
        "case_id": case["case_id"],
        "expected": case["label"],
        "verdict": verdict,
        "score": res["score"],
        "risk": res["risk"],
        "features": res["features"]
    }

async def main():
    target = "local"
    if "--target" in sys.argv:
        target = sys.argv[sys.argv.index("--target") + 1]
        
    base_dir = Path(__file__).parent.parent
    eval_dir = base_dir / "eval"
    cases_file = eval_dir / "cases.json"
    
    cases = load_cases(cases_file)
    results = []
    
    for c in cases:
        if c.get("unresolvable"):
            results.append({"case_id": c["case_id"], "expected": c["label"], "verdict": "unknown"})
            continue
        res = await evaluate_case(c)
        results.append(res)
        
    # Write to run directory
    run_dir = eval_dir / "results" / "run-001-frozen"
    run_dir.mkdir(parents=True, exist_ok=True)
    
    with open(run_dir / "results.json", "w") as f:
        json.dump(results, f, indent=2)
        
    # Generate basic metrics
    correct = sum(1 for r in results if r["expected"] == r["verdict"])
    metrics = {
        "total": len(results),
        "correct": correct,
        "accuracy": correct / len(results) if results else 0
    }
    
    with open(run_dir / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
        
    print(f"Harness completed {len(results)} cases. Accuracy: {metrics['accuracy']:.2f}")

if __name__ == "__main__":
    asyncio.run(main())
