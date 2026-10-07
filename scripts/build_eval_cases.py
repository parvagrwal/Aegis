#!/usr/bin/env python3
"""Build eval/cases.json from fired-scenario receipts.

Each receipt in the JSONL file was written by redteam/fire.py --real after a
transaction was actually mined. This script turns those receipts into eval
cases — no invented transactions, no invented labels.

Usage:
    python scripts/build_eval_cases.py --receipts redteam/fired_receipts.jsonl
    python scripts/build_eval_cases.py --receipts redteam/fired_receipts.jsonl \\
        --out eval/cases.json --force

Case schema:
    case_id       FIRE-<n>-<scenario>
    chain         e.g. "sepolia"
    tx_hash       the mined transaction hash
    label         "malicious" | "benign" (from the fired scenario)
    label_source  how the label was assigned
    attack_family e.g. "approval_drainer", "sweeper_drain", "none"
    fired_by      tool + mode that produced the receipt
    fired_at      UTC timestamp of firing
"""

import argparse
import json
import sys
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser(description="Build eval cases from fired receipts.")
    ap.add_argument("--receipts", required=True, help="JSONL receipts from redteam/fire.py --real")
    ap.add_argument("--out", default="eval/cases.json", help="output cases file")
    ap.add_argument("--force", action="store_true", help="overwrite a non-empty cases file")
    args = ap.parse_args()

    receipts_path = Path(args.receipts)
    if not receipts_path.exists():
        print(f"ERROR: receipts file not found: {receipts_path}\n"
              f"Fire scenarios first: python redteam/fire.py --real --scenario benign_transfer",
              file=sys.stderr)
        return 2

    receipts = []
    with open(receipts_path) as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if line:
                try:
                    receipts.append(json.loads(line))
                except json.JSONDecodeError as e:
                    print(f"ERROR: {receipts_path}:{lineno}: bad JSON: {e}", file=sys.stderr)
                    return 2

    if not receipts:
        print(f"ERROR: no receipts in {receipts_path}", file=sys.stderr)
        return 2

    out_path = Path(args.out)
    if out_path.exists() and out_path.stat().st_size > 2 and not args.force:
        with open(out_path) as f:
            existing = json.load(f)
        if existing:
            print(f"ERROR: {out_path} already holds {len(existing)} cases. "
                  f"Pass --force to overwrite.", file=sys.stderr)
            return 2

    cases = []
    for i, r in enumerate(receipts, 1):
        for field in ("tx_hash", "label", "scenario"):
            if field not in r:
                print(f"ERROR: receipt {i} missing field {field!r}", file=sys.stderr)
                return 2
        cases.append({
            "case_id": f"FIRE-{i:04d}-{r['scenario']}",
            "chain": r.get("chain", "sepolia"),
            "tx_hash": r["tx_hash"],
            "label": r["label"],
            "label_source": f"redteam fired scenario '{r['scenario']}' (mined tx {r['tx_hash']})",
            "attack_family": r.get("attack_family", "unknown"),
            "fired_by": r.get("fired_by", "redteam/fire.py --real"),
            "fired_at": r.get("fired_at"),
        })

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(cases, f, indent=2)

    print(f"Wrote {len(cases)} cases to {out_path} from {len(receipts)} receipts.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
