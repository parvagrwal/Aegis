"use client"
import { useState, useEffect } from "react"
import { motion } from "motion/react"
const RE=/^0x[0-9a-fA-F]{64}$/
// Default specimen: a REAL malicious case from the eval dataset (Euler Finance hack).
const DEFAULT_HASH="0xc310a0affe2169d1f6feec1c63dbc7f7c62a887fa48795d327d4d2da2d6b111d"
export default function ScanConsole({onScan, loading}:{onScan:(h:string,c:number)=>void, loading:boolean}){
  const [hash,setHash]=useState(DEFAULT_HASH)
  const [chain,setChain]=useState(11155111)
  const [err,setErr]=useState("")
  const valid=RE.test(hash.trim())
  const submit=()=>{
    if(!valid){ setErr("unrunnable: invalid hash — expected 0x + 64 hex"); return }
    setErr(""); onScan(hash.trim(), chain)
  }
  useEffect(()=>{
    const h=(e:KeyboardEvent)=>{ if((e.metaKey||e.ctrlKey) && e.key==="Enter") submit() }
    window.addEventListener("keydown",h); return()=>window.removeEventListener("keydown",h)
  })
  useEffect(()=>{
    const fill=(e:any)=>{ if(e.detail) setHash(e.detail) }
    window.addEventListener("aegis:fill" as any, fill)
    const scan=()=> submit()
    window.addEventListener("aegis:scan" as any, scan)
    return()=>{ window.removeEventListener("aegis:fill" as any, fill); window.removeEventListener("aegis:scan" as any, scan) }
  })
  return (
    <div className="card bg-panel border border-line p-4">
      <div className="mono text-[11px] tracking-[0.16em] text-brass mb-3">SPECIMEN ID</div>
      <div className="space-y-3">
        <input value={hash} onChange={e=>setHash(e.target.value)} placeholder="0x... (transaction hash)"
          className="w-full h-12 px-3 rounded-md bg-inset border border-line mono text-[13px] text-cream placeholder:text-sage/50 focus:border-line-strong focus:outline-none"
          style={{boxShadow:"inset 0 1px 0 rgba(255,255,255,0.04)"}}
        />
        {/* segmented chain */}
        <div className="grid grid-cols-2 gap-1 p-1 rounded-md bg-inset border border-line">
          {[11155111,1].map(c=>(
            <button key={c} onClick={()=>setChain(c)}
              className={`h-9 rounded-sm mono text-xs tracking-widest ${chain===c?"bg-brass text-black font-bold":"text-sage hover:text-cream"}`}>
              {c===11155111?"SEPOLIA (11155111)":"MAINNET (1)"}
            </button>
          ))}
        </div>
        <motion.button onClick={submit} disabled={loading || !valid}
          whileTap={{scale:0.98}} whileHover={{scale: valid && !loading ? 1.01:1}}
          className="w-full h-12 rounded-md bg-brass text-black font-black tracking-[0.14em] disabled:opacity-40 disabled:cursor-not-allowed hover:bg-brass-bright flex items-center justify-center gap-2">
          {loading ? <span className="w-5 h-5 border-2 border-black/20 border-t-black rounded-full animate-spin"/> : <>SCAN →</>}
        </motion.button>
        {err && <div className="mono text-xs text-pink">· {err}</div>}
      </div>
    </div>
  )
}
