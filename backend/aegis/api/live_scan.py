"""
live_scan.py — evaluate ANY EVM transaction hash live against the real chain.

Pipeline (identical to eval/harness.py::evaluate_case):
    fetch tx + receipt (RPC) -> decode -> effects -> simulate (best-effort)
    -> net_flows -> roles -> profiles (best-effort) -> intel labels
    -> CaseContext -> triage -> extract_features -> assess_case (policy.v1)
    -> verdict

Honesty rules (same as the harness):
  - Anything that fails to fetch or evaluate raises Unrunnable — never faked.
  - No answer key: the result carries no expected/correct fields.
  - RPC credentials come from the environment only, never from code or chat.
"""
import asyncio
import json
import os
import re
import time
from pathlib import Path

from aegis.chain.budget import CuBudget
from aegis.chain.decoder import decode_tx
from aegis.chain.effects import effects_from_logs, net_flows
from aegis.chain.explorer import ExplorerClient
from aegis.chain.rpc import BudgetExceeded, RpcClient, RpcError
from aegis.chain.simulate import simulate
from aegis.detect.features import extract_features
from aegis.detect.profile import get_profile
from aegis.detect.roles import determine_roles
from aegis.detect.triage import triage
from aegis.models.case import CaseContext
from aegis.policy.engine import assess_case
from aegis.util.ratelimit import TokenBucket

HASH_RE = re.compile(r"^0x[0-9a-fA-F]{64}$")

# Chain IDs this service knows how to reach.
CHAINS = {1: "ethereum", 11155111: "sepolia"}

_INTEL_ADDRESSES: dict | None = None


class Unrunnable(Exception):
    """The transaction cannot be evaluated against real chain data."""


class LiveScanUnavailable(Exception):
    """No RPC credentials configured — live scanning is disabled."""


def _intel_addresses() -> dict:
    global _INTEL_ADDRESSES
    if _INTEL_ADDRESSES is None:
        _INTEL_ADDRESSES = {}
        p = Path(__file__).resolve().parents[3] / "eval" / "intel" / "attacker_addresses.json"
        try:
            for entry in json.loads(p.read_text()):
                addr = (entry.get("address") or "").lower()
                if addr:
                    _INTEL_ADDRESSES[addr] = entry
        except Exception:
            pass
    return _INTEL_ADDRESSES


def rpc_url_for_chain(chain_id: int) -> str:
    """Resolve an RPC endpoint from the environment. Raises LiveScanUnavailable."""
    env_names = {1: "MAINNET_RPC_URL", 11155111: "SEPOLIA_RPC_URL"}
    direct = os.environ.get(env_names[chain_id], "")
    if direct:
        return direct
    key = os.environ.get("ALCHEMY_API_KEY", "")
    if key:
        host = "eth-mainnet" if chain_id == 1 else "eth-sepolia"
        return f"https://{host}.g.alchemy.com/v2/{key}"
    raise LiveScanUnavailable(
        "live scan unavailable: set MAINNET_RPC_URL / SEPOLIA_RPC_URL or "
        "ALCHEMY_API_KEY in the backend .env (use a fresh key)"
    )


def _build_rpc(url: str) -> RpcClient:
    # Demo-friendly budget: no hard monthly cap here (env ALCHEMY_MONTHLY_CU
    # governs the account side); modest rate limit to stay polite.
    budget = CuBudget(daily_limit=0, monthly_limit=0)
    bucket = TokenBucket(rate_per_s=5.0, burst=10)
    return RpcClient(url, budget, bucket)


async def _fetch_tx(rpc: RpcClient, tx_hash: str):
    try:
        tx = await rpc.call("eth_getTransactionByHash", [tx_hash], cu_cost=26, priority=1)
        receipt = await rpc.call("eth_getTransactionReceipt", [tx_hash], cu_cost=26, priority=1)
    except (RpcError, BudgetExceeded) as e:
        raise Unrunnable(f"RPC fetch failed: {e}")
    if not tx:
        raise Unrunnable("transaction not found on chain (not yet mined or wrong hash)")
    return tx, receipt or {}


async def live_scan(tx_hash: str, chain_id: int, timeout_s: float = 100.0) -> dict:
    """
    Run the full deterministic pipeline on a live transaction.
    Returns a harness-shaped result dict (no expected/correct — no answer key).
    Raises Unrunnable / LiveScanUnavailable on any honest failure.
    """
    if not HASH_RE.match(tx_hash or ""):
        raise Unrunnable("invalid hash — expected 0x + 64 hex")
    if chain_id not in CHAINS:
        raise Unrunnable(f"chain_id {chain_id} not wired (only 1 and 11155111)")

    return await asyncio.wait_for(_live_scan_inner(tx_hash, chain_id), timeout=timeout_s)


async def _live_scan_inner(tx_hash: str, chain_id: int) -> dict:
    rpc = _build_rpc(rpc_url_for_chain(chain_id))
    try:
        t0 = time.perf_counter()
        tx, receipt = await _fetch_tx(rpc, tx_hash)
        t_fetch = time.perf_counter() - t0

        t1 = time.perf_counter()
        decoded = decode_tx(tx)
        effects = effects_from_logs(receipt.get("logs", []))

        # Approval effects fixup (same as harness).
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
                    "usd_cents": -1,
                })

        try:
            sim = await simulate(rpc, tx, "latest", priority=1)
            sim_path = sim.path
        except Exception as e:  # simulate must never fake a result
            sim, sim_path = None, f"error: {e}"

        flows = net_flows(effects)
        subject, initiator = determine_roles(tx, decoded, effects, [])

        # Profiles: best-effort, never fatal. Bytecode check works without an
        # explorer key; explorer enrichment only if ETHERSCAN_API_KEY is set.
        involved: set = {tx.get("from")}
        if tx.get("to"):
            involved.add(tx.get("to"))
        for eff in effects:
            if "to" in eff:
                involved.add(eff["to"])
            if "from_" in eff:
                involved.add(eff["from_"])
        involved = {a for a in involved if a and a != "0x"
                    and a != "0x0000000000000000000000000000000000000000"}

        profile_targets = list({a for a in
                                ([tx.get("from"), tx.get("to")] +
                                 [e.get("to") for e in effects[:8] if e.get("to")])
                                if a and a != "0x"
                                and a != "0x0000000000000000000000000000000000000000"})[:8]

        profiles: dict = {}
        if profile_targets:
            explorer = ExplorerClient()
            sem = asyncio.Semaphore(5)

            async def _prof(addr: str):
                async with sem:
                    try:
                        return addr, dict(await get_profile(
                            rpc, explorer, addr, tx.get("blockNumber", "latest")))
                    except Exception:
                        return addr, {}

            for addr, prof in await asyncio.gather(*(_prof(a) for a in profile_targets)):
                profiles[addr] = prof

        intel = _intel_addresses()
        labels = {}
        for addr in involved:
            hit = intel.get((addr or "").lower())
            if hit:
                labels[addr] = {"labels": ["malicious"],
                                "provenance": hit.get("provenance", "")}

        ctx = CaseContext(
            case_id=tx_hash,
            tx={k: tx.get(k) for k in ("from", "to", "input", "value", "type", "gas", "nonce")},
            decoded=dict(decoded),
            sim=None,
            effects=[dict(e) for e in effects],
            sig_effects=[],
            net_flows={k: dict(v) for k, v in flows.items()},
            subject=subject or tx.get("from", ""),
            initiator=initiator or tx.get("from", ""),
            profiles=profiles,
            labels=labels,
        )

        triage_status = triage(ctx)
        feats = extract_features(ctx)
        res = assess_case(feats)
        t_pipeline = time.perf_counter() - t1

        risk = res["risk"]
        verdict = "malicious" if risk in ("HIGH", "CRITICAL") \
            else "uncertain" if risk == "ELEVATED" else "benign"

        return {
            "case_id": tx_hash,
            "chain": str(chain_id),
            "tx_hash": tx_hash,
            "block_number": tx.get("blockNumber"),
            "status": "runnable",
            "verdict": verdict,
            "risk": risk,
            "score": res["score"],
            "calibrated_score": res.get("calibrated_score"),
            "temperature": res.get("temperature"),
            "features": res["features"],
            "effects": [e if isinstance(e, dict) else getattr(e, "to_dict", lambda: e)() for e in effects] if effects else [],
            "triage": triage_status,
            "sim_path": sim_path,
            "timings": {
                "t_fetch_s": round(t_fetch, 3),
                "t_pipeline_s": round(t_pipeline, 3),
            },
        }
    finally:
        try:
            await rpc.client.aclose()
        except Exception:
            pass
