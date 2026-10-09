"use client"
import { useEffect, useState } from "react"
import { motion, AnimatePresence } from "motion/react"
import { springs } from "@/lib/motion-tokens"

function Typewriter({ text, speed=10 }: { text:string, speed?:number }) {
  const [out,setOut]=useState("")
  useEffect(()=>{
    if(!text) return
    setOut("")
    let i=0
    const id=setInterval(()=>{
      i+=2
      setOut(text.slice(0,i))
      if(i>=text.length) clearInterval(id)
    }, speed)
    return()=>clearInterval(id)
  },[text,speed])
  return <span className="break-all whitespace-pre-wrap">{out}</span>
}

function CopyBtn({ value }: { value:string }) {
  const [c,setC]=useState(false)
  return (
    <button
      onClick={async()=>{ await navigator.clipboard.writeText(value); setC(true); setTimeout(()=>setC(false),1400)}}
      className="shrink-0 h-7 px-2.5 rounded-full bg-[#0A0E0B] border border-line text-brass mono text-[11px] tracking-widest hover:bg-panel-raised active:scale-[0.98]"
    >
      {c?"COPIED":"COPY"}
    </button>
  )
}

export default function EvidenceScroll({ payload, signature, anchorTx }: { payload:string, signature?:string, anchorTx?:string }) {
  const stamped = Boolean(signature)
  const [typed,setTyped]=useState(false)
  useEffect(()=>{
    if(!payload) return
    const t=setTimeout(()=>setTyped(true), Math.min(payload.length*6 + 400, 1800))
    return()=>clearTimeout(t)
  },[payload])

  if(!payload && !stamped){
    return <div className="rounded-md border border-dashed border-line bg-transparent p-4 mono text-sm text-sage">UNSEALED — no signing key configured on the server.</div>
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-3">
        <span className="mono text-[11px] tracking-[0.16em] text-brass">EVIDENCE SCROLL</span>
        <AnimatePresence>
          {stamped && typed && (
            <motion.span
              key="stamped"
              initial={{scale:0.7, rotate:-12, opacity:0}}
              animate={{scale:1, rotate:-8, opacity:1}}
              transition={springs.snappy}
              className="mono text-[11px] font-black tracking-widest bg-brass text-black px-2.5 py-1 rounded-full border border-brass-bright shadow-[0_2px_10px_rgba(212,175,55,0.35)]"
            >
              ✓ STAMPED
            </motion.span>
          )}
        </AnimatePresence>
      </div>

      {/* PAYLOAD */}
      <div className="rounded-lg bg-inset border border-line p-3">
        <div className="mono text-[11px] tracking-widest text-sage mb-2">PAYLOAD</div>
        <div className="rounded-md bg-[#080A09] border border-white/[0.06] p-3 flex gap-3 items-start">
          <div className="mono text-[12px] leading-5 text-cream/90 flex-1 min-w-0">
            <Typewriter text={payload} speed={9} />
          </div>
          <CopyBtn value={payload} />
        </div>
      </div>

      {/* SIGNATURE */}
      <div className="rounded-lg bg-inset border border-line p-3">
        <div className="mono text-[11px] tracking-widest text-sage mb-2">SIGNATURE</div>
        {stamped ? (
          <div className="rounded-md bg-[#080A09] border border-white/[0.06] p-3 flex gap-3 items-start">
            <div className="mono text-[12px] leading-5 text-cream/90 flex-1 min-w-0 break-all">
              <Typewriter text={signature!} speed={7} />
            </div>
            <CopyBtn value={signature!} />
          </div>
        ) : (
          <div className="flex items-center gap-3">
            <AnimatePresence>
              {typed && (
                <motion.span
                  key="unsealed"
                  initial={{scale:1.6, rotate:-14, opacity:0}}
                  animate={{scale:1, rotate:-8, opacity:1}}
                  transition={springs.snappy}
                  className="mono text-[11px] font-black tracking-[0.2em] px-3 py-1.5 rounded-md border-2 border-dashed border-brass/60 text-brass/90"
                >
                  UNSEALED
                </motion.span>
              )}
            </AnimatePresence>
            <div className="mono text-xs text-sage">insert signing key to seal.</div>
          </div>
        )}
      </div>

      {/* ANCHOR */}
      {anchorTx && (
        <div className="rounded-lg bg-inset border border-line p-3">
          <div className="mono text-[11px] tracking-widest text-sage mb-2">ANCHOR TX (SEPOLIA)</div>
          <div className="rounded-md bg-[#080A09] border border-white/[0.06] p-3 flex gap-3 items-center">
            <a href={`https://sepolia.etherscan.io/tx/${anchorTx}`} target="_blank" className="mono text-[12px] text-brass hover:text-brass-bright break-all flex-1 underline-offset-4 hover:underline">
              {anchorTx}
            </a>
            <CopyBtn value={anchorTx} />
          </div>
        </div>
      )}

      {/* WAX SEAL - only when stamped */}
      <AnimatePresence>
        {stamped && typed && (
          <motion.div
            initial={{opacity:0, y:12, scale:0.96}}
            animate={{opacity:1, y:0, scale:1}}
            transition={springs.gentle}
            className="relative mt-2 flex justify-center py-6"
          >
            <div className="absolute top-0 inset-x-0 h-[1px] border-t border-dashed border-brass/15" />
            {/* distressed woodcut seal */}
            <div className="w-[148px] h-[148px] rounded-full grid place-items-center border-[3px] border-brass bg-brass/10 backdrop-blur shadow-[0_0_30px_rgba(212,175,55,0.25)]" style={{transform:"rotate(-12deg)"}}>
              <svg viewBox="0 0 100 100" className="absolute inset-0 w-full h-full opacity-40">
                <circle cx="50" cy="50" r="46" fill="none" stroke="#D4AF37" strokeWidth="1.2" strokeDasharray="2 3" />
                <circle cx="50" cy="50" r="38" fill="none" stroke="#D4AF37" strokeWidth="0.7" opacity="0.5"/>
              </svg>
              <div className="w-[118px] h-[118px] rounded-full border border-brass/30 grid place-items-center text-center p-2 bg-black/10">
                <div className="mono font-black leading-none">
                  <div className="text-brass text-[12px] tracking-[0.18em]">AEGIS</div>
                  <div className="text-brass text-[10px] tracking-[0.22em] mt-1">SEALED</div>
                  <div className="text-sage text-[8px] tracking-widest mt-2">SEPOLIA · ATTESTED</div>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
