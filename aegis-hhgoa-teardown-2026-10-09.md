# Why AEGIS Won't Win Hacker House Goa 2026

**Estimated score against the judging weights: 35/100.**

The eval methodology is genuinely honest. Everything around it is not ready. A judge who reads code, curls an endpoint, or opens `results.json` will find the gaps in minutes. Here they are, ordered by how fast they kill you.

---

## Kill shots (a judge finds these in under 5 minutes)

### 1. The backend doesn't boot
`pip install -r backend/requirements.txt && uvicorn backend.aegis.main:app` crashes on `ImportError` — `python-dotenv` and `rlp` aren't in requirements. The first thing a technical judge tries fails.

### 2. The case API is a hardcoded fake
`GET /api/v1/cases/{anything}` returns `verdict="malicious"`, `risk="HIGH"`, `explanation="Flagged"` — for every input, including benign cases and garbage strings. This is mock data in the demo path, the exact thing the README says is prohibited. (`backend/aegis/main.py:24-32`)

### 3. The 97.6% headline inverts on inspection
The confusion matrix from `eval/results/run-final/results.json`:

| | → benign | → uncertain | → malicious |
|---|---|---|---|
| **malicious (113)** | 3 | **102** | **8** |
| **benign (260)** | 239 | 18 | 3 |

Of 113 runnable malicious cases, **8 are called malicious (7% recall)**. 102 are punted to "uncertain." The 97.6% is accuracy on the cases the system dares to decide — and 96% of those are benign. A judge computes this in ten seconds. For a *defense* system, 7% attack recall is disqualifying no matter how the metric is framed.

### 4. A fake 100% result sits unmarked in the repo
`eval/results/final/metrics.json` claims `{"total": 30, "correct": 30, "accuracy": 1.0}` backed by 2 hand-written rows. No quarantine markers exist anywhere in the pushed repo. A judge browsing `eval/results/` finds what looks like a fabricated perfect score.

### 5. Defense never defends
`defend/actions.py` is empty (0 bytes). `executor.py` flips a dict string to `"executed"` and returns success — no transaction is built, signed, or broadcast. The approval queue's 2FA is hardcoded `"1234"` with the comment "Dummy 2FA code for testing." The one real revocation tool (`agent/tools.py`) is never called by the defense path. Defense is worth 20 points.

---

## Structural failures (found in 15 minutes of code reading)

### 6. There is no agent
`agent/planner.py` is five lines: `await asyncio.sleep()` then return a hardcoded dict. The orchestrator is a timeout wrapper. Memory's `add_anchor` is `pass`. The LLM router is empty. It's a linear scoring pipeline wearing agent filenames. Agentic engineering is worth 15 points.

### 7. The narrator is mocked
`agent/narrator.py::_call_llm()` returns its input prompt unchanged; the code comment says `# Mock LLM generation`. `agent/explain.py` is empty (0 bytes). The "LLM only writes prose" half of the design philosophy is vapor.

### 8. Attestation anchors zeros
`api/routes_scan.py:41` sets `record_hash = b"0" * 32`. The "tamper-evident log of every verdict" is tamper-evident zeros. `attest/verify.py` and `attest/store.py` are empty — there's no way to verify anything with repo tooling.

### 9. 34 of ~80 backend files are 0 bytes
Empty: all of `ingest/` (bus, evm_poll, evm_ws, firehose, solana_ws, watchlist), the case/defend API routes, `ws.py`, `auth.py`, `deps.py`, `solana_detect.py` (despite "Solana" in the project title), `anchor_sol.py`, `verify.py`, most of `util/`. The single squashed commit message claims "real NLP integration, agentic revocations, solana RPC, and crypto attestations" — substantially not implemented.

### 10. No voice console exists
Zero Web Speech API code anywhere in the repo. Voice was a merged Task 5 requirement. It's not built.

### 11. The frontend is a replay, not a system
It loops 373 historical cases on a 2.4-second timer (`NEXT_PUBLIC_FEED_MODE=replay`). "Scan" is a database lookup against the October eval — any new hash gets a 404 or 503. The threat intel (51 addresses, one of the two features behind the score) is shipped with the frontend but never wired into scans (`intel: []` hardcoded). A green pulsing "live" dot sits next to small "replay" text.

### 12. Frontend and backend were built blind to each other
`frontend/API_CONTRACT.md` says "If the FastAPI backend is ever implemented" — the frontend team wrote a speculative contract without reading the backend that already existed.

---

## Integrity problems (the honest-eval story has holes)

### 13. Native ETH is always priced at a hardcoded $2500
A string mismatch in `detect/features.py` (`get_token_price_and_decimals("eth_price")` never matches the `0xeeee...` branch) means the CoinGecko ETH branch never executes. The "$10M threshold with historical prices" claim is false for every native-ETH transfer. For 2022-era hacks (ETH ~$1,200–1,600), this overstates values by 60–100%.

### 14. Six errors, sold as three
The narrative is "3 misses." The file shows 6 decisive errors — three benign→malicious false positives from `sweeper_pattern` (which flags on any `0xff` byte in bytecode, i.e., nearly everything) are undocumented anywhere.

### 15. The scope-edge rationale exists nowhere in the repo
The $10M threshold decision, the reason the 3 misses are acceptable — it's in conversation, not in any committed file. `miss_report.py` is stale (reads a nonexistent directory). A judge can't verify the story.

### 16. Benign labels are "assumed benign"
All 260 benign cases are labeled benign because they weren't in incident reports — absence of evidence, not evidence of absence.

---

## Presentation failures

### 17. README has rendering bugs on the money slide
"$10M" is eaten by markdown (renders as "more than  strictly trigger"). Incident names have missing words ("the  Wormhole Hack"). This is the first file a judge reads.

### 18. One squashed commit
No development history. For a project whose brand is verifiability and honest process, the git history shows neither.

### 19. No demo path for a judge
No voice, no live defense, live scan needs RPC keys the judge doesn't have, the eval can't be reproduced without keys. What's demoable is the replay frontend — well-built, honestly labeled in its docs, and the strongest part of the repo.

### 20. Nothing is actually novel
Weighted-sum scoring, a 51-address blocklist, a single $10M threshold, a hash-chained log. The honest methodology is admirable but it's methodology, not innovation — and judges score the artifact.

---

## What's genuinely real (credit where due)

- The eval harness really fetches real transactions from chain.
- The 374 cases are real with real provenance and incident attribution.
- The attestor contract is real Solidity, deployed on Sepolia.
- The price cache and decimal cache are real data.
- The frontend is well-crafted and its docs are unusually honest about the replay.
- The refusal to tune the $10M threshold was the right call.
- Feature weights and the policy engine pipeline are genuine implementations.

None of that is enough.

---

## The core problem

The 97.6% belongs to the eval harness. The backend as shipped cannot boot, cannot serve it, cannot defend, cannot explain, and cannot attest. The distance between the number and the system is visible to anyone who looks past the README.

---

*Generated 2026-10-09 from a full line-by-line audit of https://github.com/parvagrwal/Aegis (371 files, 4 parallel audit passes: backend integrity, frontend integrity, eval integrity, judging-criteria gap analysis).*
