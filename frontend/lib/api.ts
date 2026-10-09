import { ScanResult } from "./types"
export async function scanTx(hash:string, chainId:number): Promise<ScanResult>{
  const r=await fetch(`/api/v1/scan`,{method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({tx_hash:hash, chain_id:chainId})})
  if(!r.ok) throw new Error((await r.json()).error || "scan failed")
  return r.json()
}
