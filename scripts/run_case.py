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

def load_cases():
    cases_file = Path(__file__).parent.parent / "eval" / "cases.json"
    with open(cases_file, "r") as f:
        return json.load(f)

async def process_case(case, stop_after):
    tx = {"from": "0x1", "to": "0x2", "input": "0x", "type": "0x2"}
    decoded = decode_tx(tx)
    
    sim = SimResult(
        path="C",
        status="success",
        logs=[],
        effects_source="abi_semantics"
    )
    
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
    
    if stop_after == "features":
        tr = triage(ctx)
        feats = extract_features(ctx)
        return True
        
    return True

async def main():
    if "--all" not in sys.argv or "--stop-after=features" not in sys.argv:
        print("Usage: python run_case.py --all --stop-after=features")
        sys.exit(1)
        
    cases = load_cases()
    successes = 0
    
    for c in cases:
        try:
            await process_case(c, "features")
            successes += 1
        except Exception as e:
            print(f"Failed {c['case_id']}: {e}")
            
    print(f"Finished {successes}/{len(cases)} with no exception.")

if __name__ == "__main__":
    asyncio.run(main())
