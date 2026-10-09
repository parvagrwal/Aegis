"use client"
import { useEffect, useState } from "react"
export default function HealthPage(){
  const [data,setData]=useState<any>(null)
  const [err,setErr]=useState("")
  useEffect(()=>{ fetch("/api/v1/health").then(r=>r.json()).then(setData).catch(e=>setErr(String(e))) },[])
  const ok=data?.status==="ok"
  return (
    <>
      <aside className="hidden lg:block" />
      <section className="card bg-panel border border-line p-6">
        <div className="flex items-center gap-3 mb-4">
          <span className={`w-3 h-3 rounded-full ${ok?"bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.5)]":err?"bg-pink shadow-[0_0_10px_rgba(255,26,94,0.4)]":"bg-brass animate-pulse"}`} />
          <h1 className="font-display font-bold tracking-widest text-brass">HEALTH</h1>
          <span className="mono text-xs text-sage">{ok?"operational":err?"error":"checking…"}</span>
        </div>
        {err && <div className="mono text-sm text-pink mb-3">{err}</div>}
        <pre className="mono text-xs leading-5 bg-inset border border-line rounded-md p-4 overflow-auto">
          {data? JSON.stringify(data,null,2) : "loading /api/v1/health …"}
        </pre>
      </section>
      <aside className="hidden lg:block" />
    </>
  )
}
