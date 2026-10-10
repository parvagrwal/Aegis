# Aegis Architecture

Aegis is a deterministic, multi-family policy engine and active defense orchestrator designed to intercept and prevent malicious Web3 transactions in real-time. The system relies entirely on on-chain RPC data and deterministic logic rather than opaque ML models.

## 1. The Policy Engine
The core of Aegis is its deterministic policy engine (`backend/aegis/policy/engine.py`), which maps atomic features into risk scores. To prevent false positives from single, heavily-weighted heuristics, the engine groups features into three categorical families:
- **BEHAVIORAL:** Features derived from transaction simulation (e.g., unlimited approvals to EOAs, 100% portfolio outflow).
- **CODE:** Features derived from smart contract bytecodes (e.g., unverified sweeper patterns).
- **INTEL:** Features derived from known threat intelligence and graph clustering (e.g., matching known attacker addresses or shared infrastructure).

### Scoring Rules
- **Hard Caps:** Each family has a hard cap of 2000 points. If multiple BEHAVIORAL features trigger (totaling 4500 points), the family only contributes 2000 points to the final score, preventing any single domain from overwhelmingly skewing the verdict.
- **The Two-Family Rule:** A critical gating mechanism. For a transaction to reach the `HIGH` (malicious) risk tier (score >= 2000), it *must* have contributing features from at least two distinct families. If a transaction scores >= 2000 but only triggers features from one family, the score is penalized by -500 and strictly capped at the `ELEVATED` (uncertain) tier. This forces the system to require corroborating evidence (e.g., BEHAVIORAL + INTEL) before classifying a transaction as malicious.

## 2. Active Defense Orchestrator
When a transaction is conclusively labeled `malicious`, Aegis engages its Active Defense Orchestrator (`backend/aegis/agent/orchestrator.py`).
- **Asynchronous Loop:** The orchestrator spins up as a detached `asyncio` task so it does not block the API response. 
- **Database Queue:** It writes a proposed defensive action (e.g., `REVOKE_APPROVAL`) to a local SQLite database (`queue.db`) and enters a 60-second polling loop awaiting manual intervention by an authorized commander.
- **Executor Integration:** Once the `status` in the queue is flipped to `approved`, the orchestrator routes the action to the Executor. The Executor constructs the actual on-chain transaction (e.g., calling `approve(spender, 0)` on the token contract), signs it using the loaded `DEFENDER_PRIVATE_KEY`, and broadcasts it to the network via RPC, effectively neutralizing the threat live on-chain.

## 3. The Detection Pipeline
The detection pipeline (`backend/aegis/api/live_scan.py` and `eval/harness.py`) operates sequentially:
1. **Fetch & Decode:** Retrieves the transaction and receipt from an EVM RPC node. Decodes calldata using predefined ABIs to understand the intent.
2. **Effects Mapping:** Parses log events to reconstruct the deterministic state changes (e.g., ERC20 approvals, native token transfers).
3. **Simulation Paths:** Features are extracted based on these state changes and the addresses involved.
4. **Triage:** Determines whether the transaction is an approval, a transfer, or a contract interaction.
5. **Policy Assessment:** Passes the array of triggered `Feature` objects to the Policy Engine for final scoring.

## 4. Phase 4 Attacker Graph (Union-Find)
To catch sophisticated adversaries who rotate their primary wallets, Aegis incorporates a 1-hop RPC graph clustering engine.
- **Methodology:** The system reads 51 known attacker addresses (from major incidents like the Nomad Bridge and Ronin hacks). It uses the Alchemy `alchemy_getAssetTransfers` RPC to fetch their top 20 incoming and outgoing token transfers.
- **Union-Find Clustering:** A Union-Find algorithm connects any attacker addresses that share at least one counterparty or funding source. This maps out hidden infrastructure (e.g., shared proxies, mixer deposits, or CEX funding addresses).
- **Live Integration:** This live graph powers the `infra.shared_attacker_infrastructure` feature (+1500 INTEL weight). If any scanned transaction interacts with an address that exists within the shared infrastructure of an attacker cluster, the feature fires, satisfying the INTEL family requirement and providing the necessary corroboration to block the transaction.
