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
        <ReasonTimeline items={result.reasons} /><div className="h-[1px] bg-line" />
        <EvidenceScroll payload={result.payload} signature={result.signature} anchorTx={result.anchor_tx} />

        {/* AI Analysis Block */}
        <div className="mt-4 p-3 rounded bg-inset border border-line">
            <div className="flex justify-between items-center mb-2">
                <div className="mono text-[11px] tracking-[0.16em] text-brass">AEGIS NLP ASSISTANT</div>
                <button onClick={() => {
                  const u = new SpeechSynthesisUtterance("Aegis voice console activated.");
                  window.speechSynthesis.speak(u);
                }} className="mono text-[10px] text-sage hover:text-brass">🎙️ VOICE CONSOLE</button>
            </div>
            <input 
              placeholder="Ask why this was flagged and press Enter..."
              className="w-full h-9 px-2 bg-panel border border-line rounded mono text-xs text-cream focus:outline-none focus:border-brass disabled:opacity-50"
              onKeyDown={async (e) => {
                if(e.key === "Enter") {
                  const input = e.currentTarget;
                  const q = input.value;
                  if(!q) return;
                  input.value = "Analyzing context...";
                  input.disabled = true;
                  try {
                     const res = await fetch("http://localhost:8000/api/v1/cases/" + result.payload.case_id + "/ask", {
                       method: "POST",
                       headers: {"Content-Type": "application/json"},
                       body: JSON.stringify({ question: q, context: result })
                     });
                     const data = await res.json();
                     alert("AEGIS AI:\\n\\n" + data.answer);
                     // VOICE API
                     const u = new SpeechSynthesisUtterance(data.answer);
                     window.speechSynthesis.speak(u);
                  } catch(err) {
                     alert("Error connecting to Aegis NLP API at localhost:8000. Is the backend running?");
                  } finally {
                     input.value = "";
                     input.disabled = false;
                  }
                }
              }}
            />
        </div>

        <div className="mono text-[11px] text-sage/60 pt-3 border-t border-dashed border-line">
          fetched in {(result.timings.fetched_ms/1000).toFixed(2)}s · decided in {(result.timings.decided_ms/1000).toFixed(2)}s
        </div>
      </div>
    </motion.div>
  )
}
