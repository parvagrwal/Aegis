#!/usr/bin/env python3
"""Run the liveness drill and regenerate docs/liveness-log.md.

For each redteam scenario (benign_transfer, approve_drainer, sweeper):
  1. fire the scenario for real (redteam/fire.py --real)   -> t_block
  2. fetch the tx + receipt over RPC                        -> t_obs
  3. run the real detection pipeline (eval harness)         -> t_decided, verdict
  4. anchor the verdict on-chain (AegisAttestor)             -> t_attest_confirmed
  5. verify: the attestation receipt has status 1           -> verify PASS/FAIL

Then regenerates docs/liveness-log.md. The log is a generated artifact:
DO NOT HAND-EDIT it.

Requires: AEGIS_RPC_URL (or SEPOLIA_RPC_URL), REDTEAM_KEY, ATTESTER_PRIVATE_KEY,
ALCHEMY_API_KEY, and the scenario contract addresses (see redteam/scenarios.json).
"""

import asyncio
import math
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).parent.parent
sys.path.insert(0, str(REPO / "redteam"))
sys.path.insert(0, str(REPO / "eval"))

import fire  # noqa: E402  (urllib JSON-RPC helper + FireError)
import harness  # noqa: E402  (real eval pipeline)

from aegis.attest.anchor_evm import anchor_records  # noqa: E402
from aegis.attest.record import canonical_serialize  # noqa: E402
from eth_utils import keccak  # noqa: E402
from aegis.chain.explorer import ExplorerClient

SCENARIOS = ["benign_transfer", "approve_drainer", "sweeper"]
VERDICT_INT = {"benign": 0, "malicious": 1, "uncertain": 2}


def confidence_bps(calibrated_score: float) -> int:
    """Policy's own probability, in basis points. Documented, not invented."""
    p = 1.0 / (1.0 + math.exp(-calibrated_score / 1000.0))
    return max(1, min(10000, int(round(p * 10000))))


def fire_scenario(scenario: str):
    """Run fire.py --real, timestamping broadcast and mining. Returns
    (tx_hash, t_block_s). Raises fire.FireError on failure."""
    t_broadcast = None
    t_mined = None
    tx_hash = None
    proc = subprocess.Popen(
        [sys.executable, str(REPO / "redteam" / "fire.py"),
         "--real", "--scenario", scenario],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
    )
    for line in proc.stdout:
        print(f"[fire:{scenario}] {line}", end="")
        if line.startswith("Broadcast:"):
            t_broadcast = time.perf_counter()
            tx_hash = line.split("Broadcast:")[1].split("—")[0].strip()
        if line.startswith("Mined in block"):
            t_mined = time.perf_counter()
    proc.wait()
    if proc.returncode != 0:
        raise fire.FireError(f"fire.py --real failed for {scenario} (exit {proc.returncode})")
    if not tx_hash or t_broadcast is None or t_mined is None:
        raise fire.FireError(f"could not parse broadcast/mining lines for {scenario}")
    return tx_hash, t_mined - t_broadcast


def wait_receipt(rpc_url: str, tx_hash: str, timeout_s: int = 300):
    deadline = time.perf_counter() + timeout_s
    while time.perf_counter() < deadline:
        receipt = fire.rpc(rpc_url, "eth_getTransactionReceipt", [tx_hash])
        if receipt:
            return receipt
        time.sleep(4)
    raise fire.FireError(f"no receipt for attestation tx {tx_hash} after {timeout_s}s")


async def run_drill(rpc_url: str, rpc, explorer, scenario: str, label: str) -> dict:
    row = {"scenario": scenario, "expected": label}
    try:
        tx_hash, t_block = fire_scenario(scenario)
        row.update({"tx_hash": tx_hash, "t_block_s": round(t_block, 1)})

        case = {"case_id": f"LIVE-{scenario}", "chain": "sepolia",
                "tx_hash": tx_hash, "label": label}
        res = await harness.evaluate_case(rpc, explorer, case)
        row.update({
            "verdict": res["verdict"],
            "risk": res["risk"],
            "t_obs_s": res["timings"]["t_fetch_s"],
            "t_decided_s": res["timings"]["t_pipeline_s"],
        })

        record = {
            "case_id": case["case_id"],
            "tx_hash": tx_hash,
            "verdict": res["verdict"],
            "risk": res["risk"],
            "score": res["score"],
            "decided_at": datetime.now(timezone.utc).isoformat(),
        }
        case_key = keccak(case["case_id"].encode())
        record_hash = keccak(canonical_serialize(record))
        conf = confidence_bps(res.get("calibrated_score", res["score"]))

        t0 = time.perf_counter()
        attest_tx = anchor_records([case_key], [1], [record_hash],
                                   [VERDICT_INT[res["verdict"]]], [conf])
        receipt = wait_receipt(rpc_url, attest_tx)
        t_attest = time.perf_counter() - t0
        ok = receipt.get("status") == "0x1"

        row.update({
            "t_attest_confirmed_s": round(t_attest, 1),
            "attest_tx": attest_tx,
            "verify": "PASS" if ok else "FAIL",
        })
        if not ok:
            row["note"] = f"attestation tx {attest_tx} did not confirm cleanly"
    except Exception as e:  # noqa: BLE001 — the log must record failures honestly
        row["verify"] = "FAIL"
        row["note"] = f"{type(e).__name__}: {e}"
    return row


def render_log(rows, provenance: dict) -> str:
    lines = [
        "# Liveness Log",
        "",
        "GENERATED BY scripts/run_liveness.py — DO NOT HAND-EDIT.",
        "Regenerate with: `python scripts/run_liveness.py` (requires chain keys).",
        "",
        "## Run provenance",
        "",
        f"- generated_at: {provenance['generated_at']}",
        f"- policy_version: {provenance['policy_version']}",
        f"- rpc_host: {provenance['rpc_host']}",
        f"- attestor_contract: 0x622E814975186227d21A12b105A1B7074649d6b6 (Sepolia)",
        "",
        "## Drills",
        "",
        "| scenario | tx_hash | expected | verdict | risk | t_block_s | t_obs_s | "
        "t_decided_s | t_attest_confirmed_s | attest_tx | verify |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        lines.append(
            f"| {r.get('scenario','-')} | {r.get('tx_hash','-')} | {r.get('expected','-')} | "
            f"{r.get('verdict','-')} | {r.get('risk','-')} | {r.get('t_block_s','-')} | "
            f"{r.get('t_obs_s','-')} | {r.get('t_decided_s','-')} | "
            f"{r.get('t_attest_confirmed_s','-')} | {r.get('attest_tx','-')} | "
            f"{r.get('verify','-')} |"
        )
    failed = [r for r in rows if r.get("verify") != "PASS"]
    lines += ["", "## Notes", ""]
    for r in rows:
        if r.get("note"):
            lines.append(f"- {r['scenario']}: {r['note']}")
    if not failed:
        lines.append("- All drills passed: every verdict was anchored and confirmed on-chain.")
    else:
        lines.append(f"- {len(failed)}/{len(rows)} drills FAILED — see notes above. Do not present this log as a passing run.")
    lines.append("")
    return "\n".join(lines)


async def main() -> int:
    rpc_url = os.environ.get("AEGIS_RPC_URL") or os.environ.get("SEPOLIA_RPC_URL")
    if not rpc_url:
        print("ERROR: AEGIS_RPC_URL (or SEPOLIA_RPC_URL) is not set.", file=sys.stderr)
        return 2
    for var in ("REDTEAM_KEY", "ATTESTER_PRIVATE_KEY", "ALCHEMY_API_KEY"):
        if not os.environ.get(var):
            print(f"ERROR: {var} is not set — the drill anchors real attestations, "
                  f"so it will not run without keys.", file=sys.stderr)
            return 2

    labels = {"benign_transfer": "benign", "approve_drainer": "malicious", "sweeper": "malicious"}
    rpc = harness.build_rpc(rpc_url)
    explorer = ExplorerClient()
    rows = []
    try:
        for i, scenario in enumerate(SCENARIOS):
            if i > 0:
                time.sleep(10)
            rows.append(await run_drill(rpc_url, rpc, explorer, scenario, labels[scenario]))
    finally:
        await rpc.close()
        await explorer.close()

    provenance = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "policy_version": harness.policy_version(),
        "rpc_host": harness.redact_rpc_host(rpc_url),
    }
    log_path = REPO / "docs" / "liveness-log.md"
    log_path.write_text(render_log(rows, provenance))
    print(f"Regenerated {log_path}")

    failed = [r for r in rows if r.get("verify") != "PASS"]
    if failed:
        print(f"{len(failed)}/{len(rows)} drills FAILED.", file=sys.stderr)
        return 1
    print("All drills passed.")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
