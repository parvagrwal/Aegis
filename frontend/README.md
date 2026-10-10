# AEGIS Vault — Obsidian & Brass

The AEGIS command deck, rebuilt as a vault: a transaction is a physical specimen
placed on a light table. You illuminate it, examine it under optics, find the
fault lines, then archive it. Quiet, material, forensic — not gamer RGB.

Pink is the crack in the evidence. Brass is the seal.

## Run it

```bash
npm install
npm run dev      # http://localhost:3000
```

Deploy: push to Vercel (free tier). No environment variables needed.

## Live scan — any transaction hash, real verdict

The scan box does two things:

1. **Dataset fast path** — the 374 eval cases answer instantly from real data
   (`frontend/data/`).
2. **Live path** — any other valid `0x…` hash is evaluated live by the Python
   backend through the real pipeline: fetch tx + receipt from chain → decode →
   effects → simulate → features → policy.v1 → verdict. Takes ~5–15s.

### Backend setup (for live scans)

```bash
# repo root
pip install -r backend/requirements.txt
```

Create `backend/.env` (never commit it, never paste keys in chat):

```
ALCHEMY_API_KEY=<a fresh key — the old one was exposed, rotate first>
# optional overrides:
# MAINNET_RPC_URL=https://eth-mainnet.g.alchemy.com/v2/<key>
# SEPOLIA_RPC_URL=https://eth-sepolia.g.alchemy.com/v2/<key>
# ETHERSCAN_API_KEY=<for richer address profiles, optional>
```

Start it:

```bash
# repo root
uvicorn backend.aegis.main:app --port 8000
```

Point the frontend at it (optional — defaults to `http://localhost:8000`):

```
# frontend/.env.local
AEGIS_BACKEND_URL=http://localhost:8000
```

Honesty rules: unknown/unfetchable hashes return `422 unrunnable`, never a
guessed verdict. No RPC key → `503 live scan unavailable`. If the backend is
down, the UI shows the error plainly; dataset scans keep working.

## How it works

There is **no live backend** in this repo (`backend/aegis/api/*.py` are empty
placeholders). Instead, the Next.js API routes serve the **real eval dataset**
directly — every number on screen comes from `data/`:

| File | Contents |
|---|---|
| `data/results.json` | 374 cases from `eval/results/run-final` (generated 2026-10-08). Every runnable case was fetched from chain and run through decode → effects → features → policy.v1. |
| `data/cases.json` | Case metadata: incident, label, label_provenance, chain_id |
| `data/metrics.json` | Headline metrics: 94.7% decisive accuracy (90.3% overall), 373 runnable / 1 unrunnable |
| `data/policy.v1.json` | Policy bands (ELEVATED ≥ 2000, HIGH ≥ 5000, CRITICAL ≥ 8500), prior −500 |
| `data/attacker_addresses.json` | 51 known attacker addresses (not yet wired to per-scan intel — see below) |

Feature weights shown in the UI are the real ones from
`backend/aegis/detect/features.py` (e.g. `intel.label_malicious` +2500,
`code.sweeper_pattern` +3000, prior −500).

### Honesty rules baked in

- **Unknown hash → 404, never guessed.** The scan route returns
  "not in eval dataset — unrunnable, never guessed", matching the backend's own
  convention. Invalid hashes → 400.
- **No signatures in the dataset → UNSEALED.** The Evidence Scroll shows its
  honest "UNSEALED — insert signing key" state. The wax seal only renders when
  a real signature exists. Nothing is faked.
- **No WebSocket backend → labeled replay.** The Flight Board streams the 373
  real runnable cases in block order via `/api/v1/feed` and is labeled
  REPLAY. It never pretends to be a live chain feed.
- **No answer key in scans.** The evidence payload excludes `expected`/`correct`
  — a scan investigates, it doesn't peek at labels.
- **Confidence is a display normalization**, not a probability: the
  deterministic score is mapped linearly from the observed eval range
  [−500, 7000] onto 0–100. Documented in `lib/dataset.ts`.

## Screens

- `/` — Command deck: Scan Console (left rail) · Light Table results (center) · Archive drawer (right rail). ⌘K command palette, ⌘↵ scans anywhere.
- `/health` — Dataset health + provenance.

Themes: Obsidian (default) · Paper · Void — toggle in the header, persists.

## If a real backend appears later

`API_CONTRACT.md` defines the contract a FastAPI backend would implement
(`POST /api/v1/scan`, `GET /api/v1/health`, `WS /ws/feed`). To switch the
frontend to it: point `lib/api.ts` and the feed hook at the backend and delete
`app/api/v1/*`.
