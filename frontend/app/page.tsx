"use client"
import { useState } from "react"
import ScanConsole from "@/components/aegis/ScanConsole"
import FlightBoard from "@/components/aegis/FlightBoard"
import ResultsPanel from "@/components/aegis/ResultsPanel"
import IntelDrawer from "@/components/aegis/IntelDrawer"
import { ScanResult } from "@/lib/types"
import { scanTx } from "@/lib/api"

export default function Page(){
  const [result,setResult]=useState<ScanResult|null>(null)
  const [loading,setLoading]=useState(false)
  const [err,setErr]=useState("")

  const doScan=async(hash:string, chainId:number)=>{
    setLoading(true); setErr("")
    window.dispatchEvent(new CustomEvent("aegis:scanning",{detail:true}))
    try{
      const r=await scanTx(hash, chainId)
      setResult(r)
    }catch(e:any){
      setErr(e.message||"scan failed")
    }finally{ setLoading(false); window.dispatchEvent(new CustomEvent("aegis:scanning",{detail:false})) }
  }

  return (
    <>
      <aside className="space-y-4 lg:sticky lg:top-[80px] h-fit">
        <ScanConsole onScan={doScan} loading={loading} />
        {err && <div className="mono text-xs text-pink border border-pink/20 bg-pink/10 rounded-md p-2.5">· {err}</div>}
        <FlightBoard onPick={(h)=>{
          window.dispatchEvent(new CustomEvent("aegis:fill",{detail:h}))
          doScan(h, 11155111)
        }} />
      </aside>
      <section className="space-y-4 min-w-0">
        <ResultsPanel result={result} loading={loading} />
      </section>
      <aside className="lg:sticky lg:top-[80px] h-fit">
        <IntelDrawer result={result} />
      </aside>
    </>
  )
}
