/**
 * dataset.ts — the honest data layer.
 *
 * There is no live FastAPI backend in this repo (backend/aegis/api/*.py are
 * empty placeholders; main.py returns hardcoded stubs). So the Next.js API
 * routes serve the REAL eval dataset directly:
 *   data/results.json  — 374 cases from eval/results/run-final (generated 2026-10-08,
 *                          every runnable case fetched from chain, decode -> effects
 *                          -> features -> policy.v1 engine)
 *   data/cases.json    — case metadata: incident, label, label_provenance
 *   data/metrics.json  — headline metrics (97.6% decisive accuracy)
 *   data/policy.v1.json — bands + prior (weights below come from
 *                          backend/aegis/detect/features.py, the real source)
 *
 * Nothing here is invented. Unknown hashes are NOT guessed — they return
 * "not in eval dataset" (the backend's own convention: unrunnable cases are
 * excluded, never guessed).
 */
import fs from "fs"
import path from "path"
import { ScanResult, TickerEvent, Verdict } from "./types"

const DATA_DIR = path.join(process.cwd(), "data")

// Real feature weights from backend/aegis/detect/features.py
const WEIGHTS: Record<string, number> = {
  "sim.approval_unlimited_to_eoa": 2500,
  "sim.approval_to_eoa_limited": 1200,
  "sim.subject_outflow_no_inflow": 2000,
  "code.unverified": 700,
  "code.sweeper_pattern": 3000,
  "intel.label_malicious": 2500,
  "sim.large_value_transfer": 2500,
  "sim.price_unavailable": 0,
}
const PRIOR = -500
const SCORE_MIN = -500
const SCORE_MAX = 7000

interface Dataset {
  results: any[]
  cases: any[]
  metrics: any
}

let cache: Dataset | null = null

function load(): Dataset {
  if (cache) return cache
  const read = (f: string) => JSON.parse(fs.readFileSync(path.join(DATA_DIR, f), "utf8"))
  const resultsJson = read("results.json")
  cache = {
    results: resultsJson.results || [],
    cases: read("cases.json"),
    metrics: read("metrics.json"),
  }
  return cache
}

function caseMeta(txHash: string): any {
  const { cases } = load()
  const h = txHash.toLowerCase()
  return cases.find((c: any) => (c.tx_hash || "").toLowerCase() === h) || null
}

export function findResult(txHash: string): any | null {
  const { results } = load()
  const h = txHash.toLowerCase()
  return results.find((r: any) => (r.tx_hash || r.case_id || "").toLowerCase() === h && r.status !== "unrunnable") || null
}

/**
 * confidence is a DISPLAY NORMALIZATION of the deterministic score onto 0-100,
 * using the observed score range [-500, 7000] of the eval set. It is not a
 * probabilistic confidence — the engine is deterministic (score + bands).
 * Bands (policy.v1): ELEVATED >= 2000, HIGH >= 5000, CRITICAL >= 8500.
 */
export function scoreToConfidence(score: number): number {
  const c = ((score - SCORE_MIN) / (SCORE_MAX - SCORE_MIN)) * 100
  return Math.max(0, Math.min(100, Math.round(c)))
}

export function toScanResult(r: any): ScanResult {
  const meta = caseMeta(r.tx_hash || r.case_id || "")
  const features: string[] = r.features || []
  // Chain comes from cases.json (results.json has chain: null for 373/374).
  const chainId = meta?.chain_id || parseInt(r.chain, 10) || 1
  const reasons = features.map((f: string) => {
    const w = WEIGHTS[f]
    return w === undefined ? `${f} · weight unknown` : `${f} · +${w}`
  })
  if (reasons.length === 0) reasons.push(`baseline prior ${PRIOR} — no features fired`)

  const timings = r.timings || {}
  // The evidence payload is the canonical verdict record (no answer key:
  // expected/correct are deliberately excluded — a scan investigates,
  // it does not peek at labels).
  const payload = JSON.stringify({
    tx_hash: r.tx_hash,
    chain_id: chainId,
    block_number: r.block_number,
    verdict: r.verdict,
    risk: r.risk,
    score_bps: r.score,
    calibrated_score: r.calibrated_score,
    features,
    triage: r.triage,
    policy: "policy.v1",
  }, null, 1)

  return {
    tx_hash: r.tx_hash,
    chain_id: chainId,
    verdict: r.verdict as Verdict,
    confidence: scoreToConfidence(r.score),
    score_bps: r.score,
    reasons,
    payload,
    // No signature / anchor in this dataset -> EvidenceScroll renders UNSEALED honestly.
    signature: undefined,
    anchor_tx: undefined,
    timings: {
      fetched_ms: Math.round((timings.t_fetch_s || 0) * 1000),
      decided_ms: Math.round((timings.t_pipeline_s || 0) * 1000),
    },
    features,
    intel: r.features ? r.features.filter((f: any) => f === "intel.label_malicious" || (f.id && f.id.startsWith("intel"))) : [],
    risk: r.risk,
    incident: meta?.incident,
    label: meta?.label,
    label_provenance: meta?.label_provenance,
  }
}

/** Feed events: runnable cases ordered by block number (chain-chronological). */
export function feedEvents(): TickerEvent[] {
  const { results } = load()
  return results
    .filter((r: any) => r.status !== "unrunnable")
    .sort((a: any, b: any) => (a.block_number || 0) - (b.block_number || 0))
    .map((r: any) => ({
      hash: r.tx_hash,
      verdict: r.verdict as Verdict,
      confidence: scoreToConfidence(r.score),
    }))
}

export function datasetHealth() {
  const { metrics } = load()
  return {
    status: "ok",
    mode: "dataset",
    note: "No live backend connected — serving the real eval dataset directly. Every number on screen comes from eval/results/run-final (generated 2026-10-08).",
    dataset: {
      cases_total: metrics.total,
      runnable: metrics.runnable,
      unrunnable: metrics.unrunnable,
      policy: metrics.provenance?.policy_version || "policy.v1",
      generated_at: metrics.provenance?.generated_at,
      accuracy_decisive: metrics.accuracy_decisive,
      accuracy_overall: metrics.accuracy,
      uncertain_rate: metrics.uncertain_rate,
    },
  }
}

export function metricsSummary() {
  return load().metrics
}
