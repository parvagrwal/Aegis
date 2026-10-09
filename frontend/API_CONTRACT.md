# API Contract — for a future live AEGIS backend

The frontend currently serves the real eval dataset from Next.js routes
(`app/api/v1/*`). If the FastAPI backend (`backend/aegis/api/`) is ever
implemented, it should expose this contract. The frontend can then switch by
pointing `lib/api.ts` + the feed hook at the backend and deleting `app/api/v1/*`.

## POST /api/v1/scan

Request: `{ "tx_hash": "0x… (64 hex)", "chain_id": 1 }`

Response 200 — ScanResult:
```json
{
  "tx_hash": "0x…",
  "chain_id": 1,
  "verdict": "benign | malicious | uncertain",
  "confidence": 76,
  "score_bps": 5200,
  "reasons": ["code.unverified · +700", "intel.label_malicious · +2500"],
  "payload": "{…canonical evidence record…}",
  "signature": "0x… (optional — omit and the UI shows UNSEALED)",
  "anchor_tx": "0x… (optional — omit and the anchor section hides)",
  "timings": { "fetched_ms": 258, "decided_ms": 4876 },
  "features": ["code.unverified"],
  "intel": [],
  "risk": "HIGH"
}
```

Response 400 — `{ "error": "unrunnable: invalid hash — expected 0x + 64 hex" }`
Response 404 — `{ "error": "not in eval dataset — unrunnable, never guessed" }`

Notes:
- `confidence` is a 0–100 display normalization of the deterministic score
  (current mapping: linear over [−500, 7000]); document whatever mapping the
  backend uses.
- `reasons` should carry real feature weights from the policy config.
- Never return a verdict for a hash the engine didn't actually evaluate.

## GET /api/v1/health

```json
{
  "status": "ok",
  "dataset": {
    "cases_total": 374, "runnable": 373, "unrunnable": 1,
    "policy": "policy.v1", "generated_at": "2026-10-08T07:43:44.122836+00:00",
    "accuracy_decisive": 0.9762, "accuracy_overall": 0.6621, "uncertain_rate": 0.3217
  }
}
```

## WS /ws/feed (future)

The current UI replays `/api/v1/feed` (block-ordered real cases, labeled REPLAY).
A live feed would push `{ "tx_hash", "verdict", "confidence }` events over
WebSocket; the FlightBoard component accepts the same `TickerEvent` shape, so
only the transport (`hooks/use-replay-feed.ts`) needs swapping.
