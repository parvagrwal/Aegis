export type Verdict="benign"|"malicious"|"uncertain"
export interface ScanResult{
  tx_hash:string; chain_id:number; verdict:Verdict; confidence:number; // 0-100
  score_bps:number; reasons:string[]; trace?:any[]; payload:string; signature?:string; anchor_tx?:string;
  timings:{ fetched_ms:number; decided_ms:number };
  features?: string[]; intel?: any[];
  risk?: string;
  // dossier (joined from cases.json — real attribution, no invented data)
  incident?: string; label?: string; label_provenance?: string;
}
export interface TickerEvent{ hash:string; verdict:Verdict; confidence:number }
