"""POST /api/v1/scan — live deterministic scan of any EVM transaction hash."""
import asyncio

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from aegis.api.live_scan import LiveScanUnavailable, Unrunnable, live_scan

router = APIRouter()


class ScanRequest(BaseModel):
    tx_hash: str
    chain_id: int = 1


@router.post("/api/v1/scan")
async def scan(req: ScanRequest):
    import os
    try:
        result = await live_scan(req.tx_hash.strip(), req.chain_id)
    except LiveScanUnavailable as e:
        return JSONResponse({"error": str(e)}, status_code=503)
    except Unrunnable as e:
        return JSONResponse({"error": str(e)}, status_code=422)
    except asyncio.TimeoutError:
        return JSONResponse({"error": "live scan timed out after 100s -- try again"},
                            status_code=504)
                            
    # Cryptographic Attestation and Active Defense integration
    if os.environ.get("ATTESTER_PRIVATE_KEY") or os.environ.get("DEFENDER_PRIVATE_KEY"):
        try:
            import json, hashlib
            from aegis.attest.anchor_evm import anchor_records
            from aegis.agent.tools import revoke_approval
            
            # 1. Attestation
            v_map = {"benign": 0, "uncertain": 1, "malicious": 2}
            v_int = v_map.get(result.get("verdict", "benign"), 0)
            
            tx_clean = req.tx_hash.strip().replace("0x", "")
            case_key = bytes.fromhex(tx_clean.zfill(64))[:32]
            
            # FIX 8: Real record hash instead of b"0" * 32
            result_json = json.dumps(result, sort_keys=True)
            record_hash = hashlib.sha256(result_json.encode('utf-8')).digest()
            
            def do_anchor():
                try:
                    tx_hash = anchor_records([case_key], [1], [record_hash], [v_int], [10000])
                except Exception as e:
                    print(f"Attestation failed: {e}")
            
            if os.environ.get("ATTESTER_PRIVATE_KEY"):
                asyncio.create_task(asyncio.to_thread(do_anchor))
                result["attestation_status"] = "queued"
                
# 2. Active Defense (Revocation)
            if result.get("verdict") == "malicious" and os.environ.get("DEFENDER_PRIVATE_KEY"):
                from aegis.agent.orchestrator import Orchestrator
                
                event_context = result.copy()
                event_context["chain_id"] = req.chain_id
                
                async def do_defense():
                    try:
                        orchestrator = Orchestrator()
                        await orchestrator.run(event_context)
                    except Exception as e:
                        import traceback
                        traceback.print_exc()
                        print(f"Defense failed: {e}")
                asyncio.create_task(do_defense())
                result["defense_status"] = "active"
                
        except Exception as e:
            print("Setup attestation failed:", e)
            pass
            
    return result