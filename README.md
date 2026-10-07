# AEGIS: Agentic Defense System for EVM and Solana

AEGIS is an autonomous intrusion detection and active defense system for EVM and Solana networks, built with a deterministic policy engine, cryptographic attestations, graph-based pattern matching via TigerGraph, and a natural language (NLP) frontend.

Design rule, learned from the teams that beat us: **the deterministic engine decides; the LLM only writes prose.** Risk scores are triggers for investigation, never verdicts.

## Features
- **Real-Time Detection:** 4.1s detection target per case (measured as `t_decided`; see the liveness log).
- **Agentic Actions:** Safely queues transaction revocations when malicious actors attempt drainer approval patterns.
- **Cryptographic Attestations:** Case verdicts are canonically serialized and anchored to the `AegisAttestor` smart contract on Sepolia, producing tamper-evident logs.
- **Episodic Vector Memory & Graph:** Utilizes TigerGraph queries and fingerprints to track attacker infrastructure over hops, clustering similar attacks.
- **Solana Devnet:** Built-in Solana SPL logic checks.

## Setup
```bash
pip install -r backend/requirements.lock.txt
```

## Running
```bash
# Start the Backend
uvicorn backend.aegis.main:app --port 8000
```

## Eval status (honest)

**What the harness measures.** `eval/harness.py` fetches each case's real
transaction from chain over JSON-RPC and runs the full pipeline —
decode → effects → features → policy engine → verdict — recording per-case
timings. Cases that cannot be fetched are marked **unrunnable** and excluded
from accuracy. No mock data, ever.

**Current state: no valid run yet.** On 2026-10-07 the old evaluation was
removed because it measured nothing:

- the old harness fed every case the same fake empty transaction, so the
  "frozen" run was really 15/30, not 100%;
- `eval/results/final/results.json` contained 2 hand-written rows behind the
  "30/30" claim — both files are quarantined as
  `eval/results/final/*.QUARANTINED-handwritten-2026-10-07`;
- `eval/cases.json` held synthetic `0xbeef…` entries with self-assigned
  labels — deleted; the file ships empty until real scenarios are fired.

A first honest number is pending the owner's Sepolia firing (see Runbook
below).

**Reproduce:**
```bash
export AEGIS_RPC_URL="https://eth-sepolia.g.alchemy.com/v2/<key>"
python eval/harness.py
# writes eval/results/run-<UTC timestamp>/{results,metrics}.json
```

**To a first valid run** (owner, with keys):
```bash
# 1. deploy redteam contracts on Sepolia, note addresses
# 2. fire scenarios for real (writes redteam/fired_receipts.jsonl)
python redteam/fire.py --real --scenario benign_transfer
python redteam/fire.py --real --scenario approve_drainer
python redteam/fire.py --real --scenario sweeper
# 3. build cases from the receipts
python scripts/build_eval_cases.py --receipts redteam/fired_receipts.jsonl
# 4. run the harness
python eval/harness.py
# 5. (optional, needs 20+ labeled samples) fit calibration
python backend/aegis/policy/calibration.py --data eval/calibration_pairs.jsonl
# 6. regenerate the liveness log
python scripts/run_liveness.py
```

**Rule: no hand-edited numbers.** Every results file carries a provenance
block (timestamp, policy version, RPC host, runnable/unrunnable counts). The
harness is the only writer of fresh results. A documented 72% beats a
fabricated 100% — publish what you measured, including what the measurement
cannot see.
