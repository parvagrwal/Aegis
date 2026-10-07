#!/usr/bin/env python3
"""Red-team scenario firer.

Default (--dry-run): prints exactly what WOULD be broadcast. No transactions
are sent, no hashes are printed, nothing is faked.

--real: signs with REDTEAM_KEY and broadcasts over plain JSON-RPC (urllib,
stdlib only for transport), waits for the receipt, and appends a JSONL receipt
to redteam/fired_receipts.jsonl. Every required env var must be set; anything
missing aborts loudly instead of guessing.

Scenarios are defined in redteam/scenarios.json.

Usage:
    python redteam/fire.py --dry-run --scenario approve_drainer
    python redteam/fire.py --real --scenario benign_transfer
    python redteam/fire.py --real --scenario approve_drainer --receipts redteam/fired_receipts.jsonl

Env (for --real):
    SEPOLIA_RPC_URL   JSON-RPC endpoint (or AEGIS_RPC_URL)
    REDTEAM_KEY       private key of the firing account (0x-prefixed hex)
    RT_TOKEN_ADDRESS  deployed RTToken (approve_drainer)
    DRAINER_ADDRESS   drainer EOA receiving the approval (approve_drainer)
    RT_SWEEPER_ADDRESS deployed RTSweeper (sweeper)
    BENIGN_TO         recipient of the benign transfer (default: sender itself)
"""

import argparse
import json
import os
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from eth_account import Account
from eth_utils import keccak
from eth_abi import encode

CHAIN_ID = 11155111  # Sepolia
CHAIN_NAME = "sepolia"
WEI_PER_ETH = 10 ** 18

SCENARIO_META = {
    "benign_transfer": {"label": "benign", "attack_family": "none"},
    "approve_drainer": {"label": "malicious", "attack_family": "approval_drainer"},
    "sweeper": {"label": "malicious", "attack_family": "sweeper_drain"},
}


class FireError(Exception):
    pass


def rpc(url: str, method: str, params):
    payload = json.dumps({"jsonrpc": "2.0", "method": method, "params": params, "id": 1}).encode()
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
    except Exception as e:
        raise FireError(f"JSON-RPC transport failed for {method}: {e}")
    if "error" in data:
        raise FireError(f"JSON-RPC error for {method}: {data['error']}")
    return data["result"]


def require_env(name: str) -> str:
    val = os.environ.get(name)
    if not val:
        raise FireError(f"{name} is not set — refusing to guess. Set it and re-run.")
    return val


def approve_calldata(spender: str, amount: int) -> str:
    selector = keccak(b"approve(address,uint256)")[:4]
    return "0x" + (selector + encode(["address", "uint256"], [spender, amount])).hex()


def plan_scenario(scenario: str, sender: str) -> dict:
    """Return the transaction fields that WOULD be sent (no signing, no broadcast)."""
    if scenario == "benign_transfer":
        to = os.environ.get("BENIGN_TO", sender or "(REDTEAM_KEY not set)")
        return {
            "to": to,
            "value_wei": 10 ** 14,  # 0.0001 ETH
            "data": "0x",
            "description": f"plain ETH transfer of 0.0001 ETH to {to}",
        }
    if scenario == "approve_drainer":
        token = os.environ.get("RT_TOKEN_ADDRESS", "(RT_TOKEN_ADDRESS not set)")
        drainer = os.environ.get("DRAINER_ADDRESS", "(DRAINER_ADDRESS not set)")
        data = "(approve(address,uint256) calldata)" if token.startswith("(") else approve_calldata(drainer, 2 ** 256 - 1)
        return {
            "to": token,
            "value_wei": 0,
            "data": data,
            "description": f"ERC20 approve(maxUint256) on {token} to drainer {drainer}",
        }
    if scenario == "sweeper":
        sweeper = os.environ.get("RT_SWEEPER_ADDRESS", "(RT_SWEEPER_ADDRESS not set)")
        return {
            "to": sweeper,
            "value_wei": 10 ** 14,
            "data": "0x",
            "description": f"send 0.0001 ETH to RTSweeper {sweeper} (auto-forwards to sink)",
        }
    raise FireError(f"unknown scenario: {scenario!r} (see redteam/scenarios.json)")


def main() -> int:
    ap = argparse.ArgumentParser(description="Fire a redteam scenario (dry-run by default).")
    ap.add_argument("--scenario", default="benign_transfer",
                    choices=list(SCENARIO_META), help="scenario to fire")
    ap.add_argument("--dry-run", action="store_true", default=True,
                    help="print what would be sent; send nothing (default)")
    ap.add_argument("--real", action="store_true",
                    help="actually sign and broadcast the transaction")
    ap.add_argument("--receipts", default="redteam/fired_receipts.jsonl",
                    help="where to append the JSONL receipt (with --real)")
    args = ap.parse_args()

    scenario = args.scenario
    meta = SCENARIO_META[scenario]
    dry_run = not args.real

    sender = None
    if os.environ.get("REDTEAM_KEY"):
        try:
            sender = Account.from_key(os.environ["REDTEAM_KEY"]).address
        except Exception as e:
            print(f"ERROR: REDTEAM_KEY is not a valid private key: {e}", file=sys.stderr)
            return 2

    try:
        plan = plan_scenario(scenario, sender)
    except FireError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    print(f"Scenario: {scenario} (label={meta['label']}, family={meta['attack_family']})")
    print(f"Plan: {plan['description']}")

    if dry_run:
        print("DRY RUN — nothing was broadcast, no hash to report.")
        return 0

    # --real from here on
    try:
        rpc_url = os.environ.get("SEPOLIA_RPC_URL") or os.environ.get("AEGIS_RPC_URL")
        if not rpc_url:
            raise FireError("SEPOLIA_RPC_URL (or AEGIS_RPC_URL) is not set.")
        key = require_env("REDTEAM_KEY")
        acct = Account.from_key(key)
        if scenario == "approve_drainer":
            require_env("RT_TOKEN_ADDRESS")
            require_env("DRAINER_ADDRESS")
        if scenario == "sweeper":
            require_env("RT_SWEEPER_ADDRESS")

        plan = plan_scenario(scenario, acct.address)  # re-plan with real addresses
        nonce = int(rpc(rpc_url, "eth_getTransactionCount", [acct.address, "latest"]), 16)
        gas_price = int(int(rpc(rpc_url, "eth_gasPrice", []), 16) * 1.2)
        gas_limit = int(int(rpc(rpc_url, "eth_estimateGas", [{
            "from": acct.address, "to": plan["to"],
            "value": hex(plan["value_wei"]), "data": plan["data"],
        }]), 16) * 1.3)

        tx = {
            "to": plan["to"],
            "value": plan["value_wei"],
            "data": plan["data"],
            "gas": gas_limit,
            "gasPrice": gas_price,
            "nonce": nonce,
            "chainId": CHAIN_ID,
        }
        signed = acct.sign_transaction(tx)
        tx_hash = rpc(rpc_url, "eth_sendRawTransaction", [signed.raw_transaction.hex()])
        print(f"Broadcast: {tx_hash} — waiting for receipt...")

        receipt = None
        for _ in range(60):
            receipt = rpc(rpc_url, "eth_getTransactionReceipt", [tx_hash])
            if receipt:
                break
            time.sleep(3)
        if not receipt:
            raise FireError(f"no receipt for {tx_hash} after 180s — check the chain manually")

        status = receipt.get("status")
        if status != "0x1":
            raise FireError(f"transaction {tx_hash} reverted (status {status})")

        record = {
            "scenario": scenario,
            "chain": CHAIN_NAME,
            "chain_id": CHAIN_ID,
            "tx_hash": tx_hash,
            "label": meta["label"],
            "attack_family": meta["attack_family"],
            "from": acct.address,
            "to": plan["to"],
            "value_wei": plan["value_wei"],
            "block_number": receipt.get("blockNumber"),
            "fired_at": datetime.now(timezone.utc).isoformat(),
            "fired_by": "redteam/fire.py --real",
        }
        receipts_path = Path(args.receipts)
        receipts_path.parent.mkdir(parents=True, exist_ok=True)
        with open(receipts_path, "a") as f:
            f.write(json.dumps(record) + "\n")

        print(f"Mined in block {int(receipt['blockNumber'], 16)}: {tx_hash}")
        print(f"Receipt appended to {receipts_path}")
        return 0
    except FireError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
