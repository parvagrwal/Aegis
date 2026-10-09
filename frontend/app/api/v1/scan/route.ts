import { NextRequest, NextResponse } from "next/server"
import { findResult, toScanResult } from "@/lib/dataset"

export const dynamic = "force-dynamic"

const RE = /^0x[0-9a-fA-F]{64}$/

/**
 * POST /api/v1/scan
 *  1. Dataset fast path — the 374 eval cases answer instantly from real data.
 *  2. Live path — any other valid hash is evaluated live by the FastAPI
 *     backend (real decode -> effects -> features -> policy.v1 pipeline).
 * Unknown/unreachable -> honest error, never a guessed verdict.
 */
export async function POST(req: NextRequest){
  let body: any = {}
  try { body = await req.json() } catch { /* ignore */ }
  const txHash = (body.tx_hash || "").trim()
  const chainId = body.chain_id === 11155111 ? 11155111 : 1

  // 1. dataset fast path
  const found = findResult(txHash)
  if (found) return NextResponse.json(toScanResult(found))

  // 2. validate before any live work
  if (!RE.test(txHash)) {
    return NextResponse.json(
      { error: "unrunnable: invalid hash — expected 0x + 64 hex" },
      { status: 400 }
    )
  }

  // 3. live backend
  const backend = process.env.AEGIS_BACKEND_URL || "http://localhost:8000"
  const ctrl = new AbortController()
  const timer = setTimeout(() => ctrl.abort(), 90000) // live scans take 5-15s+
  try {
    const r = await fetch(`${backend}/api/v1/scan`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ tx_hash: txHash, chain_id: chainId }),
      signal: ctrl.signal,
      cache: "no-store",
    })
    const data = await r.json()
    if (!r.ok) {
      return NextResponse.json(
        { error: data.error || "live scan failed" },
        { status: r.status }
      )
    }
    return NextResponse.json(toScanResult(data))
  } catch {
    return NextResponse.json(
      { error: "live scan unavailable — backend offline. Start it (see README) or scan a hash from the eval dataset." },
      { status: 503 }
    )
  } finally {
    clearTimeout(timer)
  }
}
