"use client"
import { ScanResult } from "@/lib/types"

export default function IntelDrawer({ result }: { result: ScanResult | null }) {
  if(!result){
    return (
      <div className="card bg-panel border border-line p-4">
        <div className="mono text-[11px] tracking-[0.16em] text-brass mb-3">ARCHIVE</div>
        <div className="mono text-xs leading-5 text-sage">No specimen yet. Policy traces and intel labels will appear here after a scan.</div>
      </div>
    )
  }
  const features = result.features || []
  const intel = result.intel || []
  return (
    <div className="card bg-panel border border-line p-4 space-y-4">
      <div className="mono text-[11px] tracking-[0.16em] text-brass">ARCHIVE</div>

      {/* dossier — real attribution joined from cases.json */}
      {(result.incident || result.label) && (
        <>
          <div>
            <div className="mono text-[11px] tracking-widest text-sage mb-2">DOSSIER</div>
            <div className="space-y-1.5 mono text-[11px]">
              {result.incident && (
                <div className="px-2.5 py-2 rounded-md bg-inset border border-line text-cream">{result.incident}</div>
              )}
              <div className="flex gap-2">
                {result.label && (
                  <span className="px-2.5 py-1 rounded-full border border-line text-sage">label: {result.label}</span>
                )}
                {result.risk && (
                  <span className="px-2.5 py-1 rounded-full border border-line text-sage">risk: {result.risk}</span>
                )}
              </div>
              {result.label_provenance && (
                <div className="px-2.5 py-2 rounded-md bg-inset border border-line text-sage leading-5">{result.label_provenance}</div>
              )}
            </div>
          </div>
          <div className="h-[1px] bg-line" />
        </>
      )}

      <div>
        <div className="mono text-[11px] tracking-widest text-sage mb-2">POLICY TRACES</div>
        {features.length===0 ? <div className="mono text-xs text-sage">No traces fired.</div> : (
          <div className="space-y-1.5">
            {features.map((f:string,i:number)=>(
              <div key={i} className="mono text-[11px] px-2.5 py-2 rounded-md bg-inset border border-line text-cream flex justify-between">
                <span>{f}</span>
              </div>
            ))}
          </div>
        )}
      </div>
      <div className="h-[1px] bg-line" />
      <div>
        <div className="mono text-[11px] tracking-widest text-sage mb-2">THREAT INTEL</div>
        {intel.length===0 ? <div className="mono text-xs text-sage">No intel labels.</div> : (
          <div className="space-y-1.5">
            {intel.map((l:any,i:number)=>(
              <div key={i} className="mono text-xs flex justify-between bg-inset border border-line rounded-md px-2.5 py-2">
                <span className="text-cream">{typeof l==="string"?l: l.label||l.name}</span>
                <span className="text-sage">{typeof l?.confidence==="number"? Math.round(l.confidence*100)+"%":""}</span>
              </div>
            ))}
          </div>
        )}
      </div>
      <div className="mono text-[11px] text-sage/60 border-t border-dashed border-line pt-3">
        score_bps: {result.score_bps ?? "—"} · {(result.risk||result.verdict||"").toString()}
      </div>
    </div>
  )
}
