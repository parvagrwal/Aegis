"use client"
import { motion } from "motion/react"
import { ScanResult } from "@/lib/types"
import VerdictMonolith from "./VerdictMonolith"
import LiquidMeter from "./LiquidMeter"
import ReasonTimeline from "./ReasonTimeline"
import EvidenceScroll from "./EvidenceScroll"
import { useEffect } from "react"

export default function ResultsPanel({ result, loading }: { result: ScanResult|null, loading:boolean }) {
  useEffect(()=>{
    const c=!result ? "rgba(212,175,55,0.06)" : result.verdict==="malicious"?"rgba(255,26,94,0.10)": result.verdict==="uncertain"?"rgba(212,175,55,0.10)":"rgba(16,185,129,0.08)"
    document.documentElement.style.setProperty("--cursor-color", c)
  },[result])

  if(loading){
    return (
      <div className="card bg-panel border border-line p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-[96px] rounded-lg bg-inset" />
          <div className="h-2 rounded-full bg-inset" />
          <div className="h-24 rounded-lg bg-inset" />
        </div>
      </div>
    )
  }
  if(!result){
    return (
      <div className="card border border-dashed border-line bg-transparent p-10 text-center">
        <div className="mx-auto w-[240px] h-[96px] rounded-lg border border-line bg-panel/30 grid place-items-center mono text-xs text-sage mb-4">
          AWAITING SPECIMEN
        </div>
        <div className="mono text-sm text-sage">No scan yet. Submit a transaction hash — or press ⌘↵.</div>
        <div className="mono text-xs text-sage/60 mt-2">The light table will illuminate the verdict.</div>
      </div>
    )
  }

  return (
    <motion.div initial={{opacity:0, y:8}} animate={{opacity:1, y:0}} className="card border border-line overflow-hidden bg-panel">
      {/* perforated top edge for the whole dossier */}
      <div className="h-3 w-full opacity-40" style={{background:"radial-gradient(circle, var(--line) 1.2px, transparent 1.5px)", backgroundSize:"12px 12px", backgroundRepeat:"repeat-x"}} />
      <div className="p-4 md:p-5 space-y-5">
        <VerdictMonolith verdict={result.verdict} confidence={result.confidence} />
        <LiquidMeter value={result.confidence} />
        <ReasonTimeline items={result.reasons} />
        <div className="h-[1px] bg-line" />
        <EvidenceScroll payload={result.payload} signature={result.signature} anchorTx={result.anchor_tx} />
        <div className="mono text-[11px] text-sage/60 pt-3 border-t border-dashed border-line">
          fetched in {(result.timings.fetched_ms/1000).toFixed(2)}s · decided in {(result.timings.decided_ms/1000).toFixed(2)}s
        </div>
      </div>
    </motion.div>
  )
}
