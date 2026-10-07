#!/usr/bin/env python3
"""AEGIS evaluation harness — real pipeline only, no mocks.

Each case in eval/cases.json carries a chain and a tx_hash. The harness
fetches the transaction and its receipt over JSON-RPC, then runs the REAL
pipeline:

    fetch -> decode -> effects (from receipt logs) -> roles -> features
           -> triage -> policy engine -> verdict

Rules:
- If the RPC is unreachable or a transaction cannot be fetched, the case is
  marked "unrunnable". Fake or substitute data is NEVER used.
- Accuracy is computed on runnable cases only, and the report says so.
- results.json and metrics.json each carry a provenance block.
- The harness is the only writer of fresh results. It never edits files by hand.
- Exit code is non-zero when no case was runnable.

Env:
    AEGIS_RPC_URL   EVM JSON-RPC endpoint (e.g. Sepolia). Required.

Usage:
    python eval/harness.py [--cases eval/cases.json] [--out-dir eval/results/run-<ts>]
"""

import argparse
import asyncio
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from aegis.chain.rpc import RpcClient, RpcError, BudgetExceeded
from aegis.chain.budget import CuBudget
from aegis.util.ratelimit import TokenBucket
from aegis.models.case import CaseContext
from aegis.chain.simulate import simulate
from aegis.chain.decoder import decode_tx
from aegis.chain.effects import effects_from_logs, net_flows
from aegis.detect.roles import determine_roles
from aegis.detect.features import extract_features
from aegis.chain.explorer import ExplorerClient
from aegis.detect.profile import get_profile
from aegis.detect.triage import triage
from aegis.policy.engine import assess_case

EVM_CHAINS = {"ethereum", "sepolia", "evm"}


class Unrunnable(Exception):
    """A case that cannot be evaluated against real chain data."""


def redact_rpc_host(url: str) -> str:
    """Keep scheme + host only; API keys must never land in result files."""
    parts = urlsplit(url)
    host = parts.hostname or "unknown"
    return f"{parts.scheme}://{host}"


def policy_version() -> str:
    p = Path(__file__).parent.parent / "backend" / "config" / "policy.v1.json"
    try:
        with open(p) as f:
            return json.load(f).get("version", "unknown")
    except OSError:
        return "unknown"


def build_rpc(url: str) -> RpcClient:
    # Limits of 0 disable budget enforcement; eval is priority 1 anyway.
    budget = CuBudget(daily_limit=0, monthly_limit=0)
    bucket = TokenBucket(rate_per_s=5.0, burst=10)
    return RpcClient(url, budget, bucket)


async def fetch_case_tx(rpc: RpcClient, case: dict):
    """Fetch tx + receipt. Raises Unrunnable on any failure — never fakes data."""
    chain = case.get("chain", "")
    if chain not in EVM_CHAINS:
        raise Unrunnable(f"chain '{chain}' is not wired in this harness (EVM only so far)")
    tx_hash = case.get("tx_hash")
    if not tx_hash or not str(tx_hash).startswith("0x"):
        raise Unrunnable(f"case has no usable tx_hash: {tx_hash!r}")
    try:
        tx = await rpc.call("eth_getTransactionByHash", [tx_hash], cu_cost=26, priority=1)
        receipt = await rpc.call("eth_getTransactionReceipt", [tx_hash], cu_cost=26, priority=1)
    except (RpcError, BudgetExceeded) as e:
        raise Unrunnable(f"RPC fetch failed: {e}")
    if not tx:
        raise Unrunnable("transaction not found on chain (not yet mined or wrong hash)")
    return tx, receipt or {}


async def evaluate_case(rpc: RpcClient, explorer: ExplorerClient, case: dict) -> dict:
    t0 = time.perf_counter()
    tx, receipt = await fetch_case_tx(rpc, case)
    t_fetch = time.perf_counter() - t0

    t1 = time.perf_counter()
    decoded = decode_tx(tx)

    effects = effects_from_logs(receipt.get("logs", []))
    
    sel = decoded.get("selector")
    if sel in ("0x095ea7b3", "0x39509351"):
        args = decoded.get("args", {})
        spender = args.get("spender")
        amount = args.get("amount") if sel == "0x095ea7b3" else args.get("addedValue")
        if spender is not None and amount is not None:
            effects.append({
                "kind": "erc20_approval",
                "token": tx.get("to", ""),
                "from_": tx.get("from", ""),
                "to": spender.lower(),
                "amount": str(amount),
                "token_id": None,
                "usd_cents": -1
            })
            
    try:
        sim = await simulate(rpc, tx, "latest", priority=1)
        sim_path = sim.path
        sim = sim.model_dump() if hasattr(sim, "model_dump") else dict(sim)
    except Exception as e:  # simulate must never fake a result
        sim, sim_path = None, f"error: {e}"

    flows = net_flows(effects)
    subject, initiator = determine_roles(tx, decoded, effects, [])

    involved = {tx.get("from")}
    if tx.get("to"): involved.add(tx.get("to"))
    for eff in effects:
        if "to" in eff: involved.add(eff["to"])
        if "from_" in eff: involved.add(eff["from_"])
    involved = {a for a in involved if a and a != "0x" and a != "0x0000000000000000000000000000000000000000"}
    
    profiles = {}
    for addr in involved:
        profiles[addr] = dict(await get_profile(rpc, explorer, addr, tx.get("blockNumber", "latest")))

    ctx = CaseContext(
        case_id=case["case_id"],
        tx={k: tx.get(k) for k in ("from", "to", "input", "value", "type", "gas", "nonce")},
        decoded=dict(decoded),
        sim=None,
        effects=[dict(e) for e in effects],
        sig_effects=[],
        net_flows={k: dict(v) for k, v in flows.items()},
        subject=subject or tx.get("from", ""),
        initiator=initiator or tx.get("from", ""),
        profiles=profiles,
        labels={}, # Intel label source not yet wired in harness
    )

    triage_status = triage(ctx)
    feats = extract_features(ctx)
    res = assess_case(feats)
    t_pipeline = time.perf_counter() - t1

    if res["risk"] in ("HIGH", "CRITICAL"):
        verdict = "malicious"
    elif res["risk"] == "ELEVATED":
        verdict = "uncertain"
    else:
        verdict = "benign"

    return {
        "case_id": case["case_id"],
        "chain": case.get("chain"),
        "tx_hash": case.get("tx_hash"),
        "block_number": tx.get("blockNumber"),
        "status": "runnable",
        "expected": case.get("label"),
        "verdict": verdict,
        "correct": verdict == case.get("label"),
        "risk": res["risk"],
        "score": res["score"],
        "calibrated_score": res.get("calibrated_score"),
        "temperature": res.get("temperature"),
        "features": res["features"],
        "triage": triage_status,
        "sim_path": sim_path,
        "timings": {
            "t_fetch_s": round(t_fetch, 3),
            "t_pipeline_s": round(t_pipeline, 3),
        },
    }


async def main() -> int:
    ap = argparse.ArgumentParser(description="AEGIS eval harness (real pipeline, no mocks).")
    ap.add_argument("--cases", default=None)
    ap.add_argument("--out-dir", default=None)
    args = ap.parse_args()

    base_dir = Path(__file__).parent.parent
    cases_file = Path(args.cases) if args.cases else base_dir / "eval" / "cases.json"

    rpc_url = os.environ.get("AEGIS_RPC_URL")
    if not rpc_url:
        print("ERROR: AEGIS_RPC_URL is not set. The harness refuses to run without a "
              "real RPC endpoint — it will not substitute fake data.", file=sys.stderr)
        return 2

    try:
        with open(cases_file) as f:
            cases = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: cases file not found: {cases_file}", file=sys.stderr)
        return 2

    if not cases:
        print(f"ERROR: {cases_file} is empty. Populate it first — see eval/cases.README.md. "
              f"The harness will not invent cases.", file=sys.stderr)
        return 2

    rpc = build_rpc(rpc_url)
    explorer = ExplorerClient()
    results = []
    try:
        for c in cases:
            try:
                results.append(await evaluate_case(rpc, explorer, c))
            except Unrunnable as e:
                results.append({
                    "case_id": c.get("case_id"),
                    "chain": c.get("chain"),
                    "tx_hash": c.get("tx_hash"),
                    "status": "unrunnable",
                    "reason": str(e),
                    "expected": c.get("label"),
                })
    finally:
        await rpc.close()
        await explorer.close()

    runnable = [r for r in results if r["status"] == "runnable"]
    unrunnable = [r for r in results if r["status"] != "runnable"]
    correct = sum(1 for r in runnable if r.get("correct"))
    uncertain_count = sum(1 for r in runnable if r.get("verdict") == "uncertain")
    decisive_count = len(runnable) - uncertain_count

    generated_at = datetime.now(timezone.utc).isoformat()
    provenance = {
        "generated_by": "eval/harness.py",
        "generated_at": generated_at,
        "policy_version": policy_version(),
        "rpc_host": redact_rpc_host(rpc_url),
        "cases_total": len(results),
        "runnable": len(runnable),
        "unrunnable": len(unrunnable),
        "accuracy_basis": "runnable cases only — unrunnable cases are excluded, never guessed",
        "note": "No mock data. Every runnable case was fetched from chain and run "
                "through decode -> effects -> features -> policy engine.",
    }

    out_dir = Path(args.out_dir) if args.out_dir else (
        base_dir / "eval" / "results" / f"run-{datetime.now(timezone.utc):%Y%m%d-%H%M%S}")
    out_dir.mkdir(parents=True, exist_ok=True)

    with open(out_dir / "results.json", "w") as f:
        json.dump({"provenance": provenance, "results": results}, f, indent=2)

    metrics = {
        "total": len(results),
        "runnable": len(runnable),
        "unrunnable": len(unrunnable),
        "uncertain_count": uncertain_count,
        "uncertain_rate": (uncertain_count / len(runnable)) if runnable else 0.0,
        "correct": correct,
        "accuracy": (correct / len(runnable)) if runnable else None,
        "accuracy_decisive": (correct / decisive_count) if decisive_count > 0 else None,
        "accuracy_basis": "runnable cases only",
        "provenance": provenance,
    }
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"Wrote {out_dir / 'results.json'} and {out_dir / 'metrics.json'}")
    print(f"Cases: {len(results)} total, {len(runnable)} runnable, {len(unrunnable)} unrunnable, {uncertain_count} uncertain")
    if runnable:
        print(f"Accuracy (runnable only): {correct}/{len(runnable)} = {correct / len(runnable):.3f}")
        if decisive_count > 0:
            print(f"Accuracy (decisive only): {correct}/{decisive_count} = {correct / decisive_count:.3f}")
    else:
        print("NO RUNNABLE CASES — nothing was measured. Check RPC access and case tx_hashes.")
        return 1
    if unrunnable:
        print("Unrunnable cases (excluded from accuracy):")
        for r in unrunnable:
            print(f"  - {r['case_id']}: {r['reason']}")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
