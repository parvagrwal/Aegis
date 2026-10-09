"use client"
import { motion } from "motion/react"
import { ScanResult } from "@/lib/types"
import VerdictMonolith from "./VerdictMonolith"
import LiquidMeter from "./LiquidMeter"
import ReasonTimeline from "./ReasonTimeline"
import EvidenceScroll from "./EvidenceScroll"
import { useEffect, useState } from "react"

export default function ResultsPanel({ result, loading }: { result: ScanResult|null, loading:boolean }) {
  const [aiResponse, setAiResponse] = useState("");
    const [errorMsg, setErrorMsg] = useState("");
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
        
        {/* Fund Trace Block */}
        {result.trace && result.trace.length > 0 && (
          <div className="mt-4 p-3 rounded bg-inset border border-line">
            <div className="mono text-[11px] tracking-[0.16em] text-brass mb-2">MULTI-HOP FUND TRACE</div>
            {result.trace.map((tr: any, i: number) => (
              <div key={i} className="mono text-[12.5px] leading-5 text-cream/90 flex flex-col gap-1">
                <div className="text-sage">Path: <span className="text-cream">{tr.path}</span></div>
                <div className="text-sage flex gap-4">
                  <span>Hops: <span className="text-cream">{tr.hops}</span></span>
                  <span>Amount: <span className="text-cream">\</span></span>
                  <span>Confidence: <span className="text-cream">{tr.confidence}</span></span>
                </div>
              </div>
            ))}
          </div>
        )}
        
                <EvidenceScroll payload={result.payload} signature={result.signature} anchorTx={result.anchor_tx} />
        
        {/* Verification Block */}
        <div className="mt-4 p-3 rounded bg-inset border border-line">
            <div className="flex justify-between items-center mb-2">
                <div className="mono text-[11px] tracking-[0.16em] text-brass">CRYPTOGRAPHIC VERIFICATION</div>
                <button 
                  onClick={async () => {
                    const btn = document.getElementById("verify-btn") as HTMLButtonElement;
                    btn.innerText = "Verifying on Sepolia...";
                    btn.disabled = true;
                    try {
                      const backend = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";
                      const res = await fetch(backend + "/api/v1/cases/" + result.tx_hash + "/verify", {
                        method: "POST",
                        headers: {"Content-Type": "application/json"},
                        body: JSON.stringify({ question: "verify", context: result })
                      });
                      const data = await res.json();
                      const out = document.getElementById("verify-output");
                      if(out) {
                        if(data.verified) {
                            out.innerHTML = "<span class='text-[#10b981]'>? VERIFIED</span><br/>Local Hash: " + data.local_hash + "<br/>On-Chain Hash: " + data.on_chain_hash;
                        } else {
                            out.innerHTML = "<span class='text-[#ff1a5e]'>? UNVERIFIED</span><br/>" + (data.error || "Hash mismatch.");
                        }
                      }
                    } catch(e) {
                      const out = document.getElementById("verify-output");
                      if(out) out.innerHTML = "<span class='text-[#ff1a5e]'>Error connecting to backend.</span>";
                    } finally {
                      btn.innerText = "VERIFY ON-CHAIN";
                      btn.disabled = false;
                    }
                  }}
                  id="verify-btn"
                  className="mono text-[10px] bg-line text-cream hover:text-brass px-2 py-1 rounded"
                >VERIFY ON-CHAIN</button>
            </div>
            <div id="verify-output" className="mono text-[11px] text-sage break-words">
                Click verify to fetch the attestation from the AegisAttestor smart contract on Sepolia.
            </div>
        </div>


        {/* AI Analysis Block */}
        <div className="mt-4 p-3 rounded bg-inset border border-line">
            <div className="flex justify-between items-center mb-2">
                <div className="mono text-[11px] tracking-[0.16em] text-brass">AEGIS NLP ASSISTANT</div>
                <button onClick={() => {
                  if (window.speechSynthesis.speaking) {
                    window.speechSynthesis.cancel();
                  } else {
                    const u = new SpeechSynthesisUtterance("Aegis voice console ready. Ask a question to begin.");
                    window.speechSynthesis.speak(u);
                  }
                }} className="mono text-[10px] text-sage hover:text-brass">MIC VOICE CONSOLE (STOP/START)</button>
            </div>
            <div className="flex gap-2">
            <input 
              id="aegis-nlp-input"
              placeholder="Ask why this was flagged and press Enter..."
              className="w-full h-9 px-2 bg-panel border border-line rounded mono text-xs text-cream focus:outline-none focus:border-brass disabled:opacity-50"
              onKeyDown={async (e) => {
                if(e.key === "Enter") {
                  const input = e.currentTarget;
                  const q = input.value;
                  if(!q) return;
                  setErrorMsg("");
                  input.value = "Analyzing context...";
                  input.disabled = true;
                  try {
                     const backend = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";
                     const res = await fetch(backend + "/api/v1/cases/" + result.tx_hash + "/ask", {
                       method: "POST",
                       headers: {"Content-Type": "application/json"},
                       body: JSON.stringify({ question: q, context: result })
                     });
                     const data = await res.json();
                     
                     let displayText = data.answer;
                     let spokenText = data.answer;
                     if (data.answer.includes("VOICE_SUMMARY:")) {
                         const parts = data.answer.split("VOICE_SUMMARY:");
                         displayText = parts[0].trim();
                         spokenText = parts[1].trim();
                     }
                     
                     setAiResponse(displayText);
                     
                     // VOICE API
                     if (window.speechSynthesis.speaking) {
                         window.speechSynthesis.cancel();
                     }
                     const u = new SpeechSynthesisUtterance(spokenText);
                     window.speechSynthesis.speak(u);
                  } catch(err) {
                     setErrorMsg("Error connecting to Aegis NLP API. Is the backend running?");
                  } finally {
                     input.value = "";
                     input.disabled = false;
                  }
                }
              }}
            />
            <button 
              className="h-9 px-3 bg-panel border border-line rounded mono text-xs text-sage hover:text-cream"
              onClick={() => {
                const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
                if (!SpeechRecognition) return setErrorMsg("Speech recognition not supported in this browser.");
                const recognition = new SpeechRecognition();
                recognition.onresult = async (event: any) => {
                    const transcript = event.results[0][0].transcript;
                    const input = document.getElementById("aegis-nlp-input") as HTMLInputElement;
                    if (input) {
                        input.value = transcript;
                        // Execute the same logic manually since dispatchEvent fails React's synthetic system
                        const q = transcript;
                        if(!q) return;
                        setErrorMsg("");
                  input.value = "Analyzing context...";
                        input.disabled = true;
                        try {
                           const backend = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";
                           const res = await fetch(backend + "/api/v1/cases/" + result.tx_hash + "/ask", {
                             method: "POST",
                             headers: {"Content-Type": "application/json"},
                             body: JSON.stringify({ question: q, context: result })
                           });
                           const data = await res.json();
                           
                           let displayText = data.answer;
                           let spokenText = data.answer;
                           if (data.answer.includes("VOICE_SUMMARY:")) {
                               const parts = data.answer.split("VOICE_SUMMARY:");
                               displayText = parts[0].trim();
                               spokenText = parts[1].trim();
                           }
                           
                           setAiResponse(displayText);
                           
                           if (window.speechSynthesis.speaking) {
                               window.speechSynthesis.cancel();
                           }
                           const u = new SpeechSynthesisUtterance(spokenText);
                           window.speechSynthesis.speak(u);
                        } catch(err) {
                           setErrorMsg("Error connecting to Aegis NLP API. Is the backend running?");
                        } finally {
                           input.value = "";
                           input.disabled = false;
                        }
                    }
                };
                recognition.start();
              }}
            >MIC</button>
            </div>
            {aiResponse && (
                <div className="mt-3 p-3 bg-panel border border-line rounded mono text-xs text-cream/90 whitespace-pre-wrap break-words overflow-hidden">
                    {aiResponse}
                </div>
            )}
            {errorMsg && (
                <div className="mt-3 p-3 bg-panel border border-[rgba(255,26,94,0.4)] rounded mono text-xs text-[#ff1a5e] whitespace-pre-wrap break-words">
                    {errorMsg}
                </div>
            )}
        </div>

        <div className="mono text-[11px] text-sage/60 pt-3 border-t border-dashed border-line">
          fetched in {(result.timings.fetched_ms/1000).toFixed(2)}s · decided in {(result.timings.decided_ms/1000).toFixed(2)}s
        </div>
      </div>
    </motion.div>
  )
}
