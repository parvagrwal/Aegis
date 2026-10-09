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
    try:
        result = await live_scan(req.tx_hash.strip(), req.chain_id)
    except LiveScanUnavailable as e:
        return JSONResponse({"error": str(e)}, status_code=503)
    except Unrunnable as e:
        return JSONResponse({"error": str(e)}, status_code=422)
    except asyncio.TimeoutError:
        return JSONResponse({"error": "live scan timed out after 100s — try again"},
                            status_code=504)
    return result
