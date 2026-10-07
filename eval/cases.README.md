# eval/cases.json — how this file gets populated

This file intentionally ships as an **empty list**. Cases are never invented
here. Every case must trace back to a transaction that was actually mined,
fired by our own redteam tooling (or a documented historical transaction with
a verifiable hash and a cited label source).

## Case schema

| field          | meaning                                                        |
|----------------|----------------------------------------------------------------|
| `case_id`      | `FIRE-<n>-<scenario>`, e.g. `FIRE-0001-approve_drainer`         |
| `chain`        | chain the tx was mined on, e.g. `sepolia`                      |
| `tx_hash`      | the mined transaction hash (`0x…`)                              |
| `label`        | `malicious` or `benign`                                        |
| `label_source` | how the label was assigned (scenario name + tx hash)           |
| `attack_family`| e.g. `approval_drainer`, `sweeper_drain`, `none`               |
| `fired_by`     | tool and mode that produced the receipt                        |
| `fired_at`     | UTC timestamp of firing                                        |

## Populating it (owner runs these with real keys)

1. Deploy the redteam contracts on Sepolia and note the addresses:
   `RT_TOKEN_ADDRESS`, `RT_SWEEPER_ADDRESS`, `DRAINER_ADDRESS`.
2. Fire each scenario for real (writes receipts to `redteam/fired_receipts.jsonl`):
   ```bash
   python redteam/fire.py --real --scenario benign_transfer
   python redteam/fire.py --real --scenario approve_drainer
   python redteam/fire.py --real --scenario sweeper
   ```
3. Build the cases file:
   ```bash
   python scripts/build_eval_cases.py --receipts redteam/fired_receipts.jsonl
   ```
4. Run the harness:
   ```bash
   export AEGIS_RPC_URL="https://eth-sepolia.g.alchemy.com/v2/<key>"
   python eval/harness.py
   ```

## Rules

- The harness (`eval/harness.py`) fetches each `tx_hash` from chain. A case
  whose transaction cannot be fetched is marked **unrunnable** and excluded
  from accuracy — never guessed, never substituted.
- Accuracy is reported on runnable cases only, and the report says so.
- No hand-edited numbers: every results file carries a provenance block, and
  the harness is the only writer of fresh results.
- The old `0xbeef…` placeholder entries were deleted on 2026-10-07. They
  measured nothing.
