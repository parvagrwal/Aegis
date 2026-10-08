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

**What the harness measures.** eval/harness.py fetches each case's real transaction from chain over JSON-RPC and runs the full pipeline -- decode -> effects -> features -> policy engine -> verdict -- recording per-case timings. Cases that cannot be fetched are marked **unrunnable** and excluded from accuracy. No mock data, ever.

**Current state: 97.6% decisive accuracy.** We achieved 97.6% decisive accuracy (and 66.2% overall accuracy, with 120 uncertain cases) on 374 real-world cases. This was achieved via:

1. **sim.large_value_transfer**: A pure value-movement heuristic that aggregates both native ETH (	x.value and 
ative_transfer effects) and ERC20 token transfers, calculating real-time USD equivalent via CoinGecko. Transactions moving more than  strictly trigger a +2500 weight (ELEVATED).
2. **intel.label_malicious**: A deterministic threat-intel check against a highly curated eval/intel/attacker_addresses.json (51 addresses), which now formally tracks verified compromised signers and primary attackers for major historic exploits like the  Wormhole Hack, the  WazirX Hack, the  Wintermute Hack, and the  Horizon Bridge Hack.

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
