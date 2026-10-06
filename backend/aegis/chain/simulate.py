import os
from pydantic import BaseModel
from typing import Literal, Optional, Any
from aegis.chain.rpc import RpcClient

class SimResult(BaseModel):
    path: Literal["A", "B", "C"]
    status: Literal["success", "reverted", "error", "unsupported"]
    gas_used: Optional[int] = None
    return_data: Optional[str] = None
    revert_reason: Optional[str] = None
    logs: list[dict] = []
    effects_source: Literal["simulation", "receipt", "abi_semantics"]
    delegation_probe_forwards: bool = False

async def simulate(
    rpc: RpcClient,
    call: dict,
    block: int | Literal["latest"],
    *,
    priority: int
) -> SimResult:
    sim_path = os.environ.get("SIM_PATH", "A")
    block_param = hex(block) if isinstance(block, int) else block
    
    tx_obj = {
        "from": call.get("from", "0x0000000000000000000000000000000000000000"),
        "to": call.get("to"),
        "value": hex(call.get("value", 0)) if isinstance(call.get("value"), int) else call.get("value", "0x0"),
        "data": call.get("data", call.get("input", "0x")),
        "gas": hex(call.get("gas", 30000000)) if isinstance(call.get("gas"), int) else call.get("gas", "0x1c9c380")
    }
    
    # Remove None values
    tx_obj = {k: v for k, v in tx_obj.items() if v is not None}
    
    if "authorizationList" in call:
        tx_obj["authorizationList"] = call["authorizationList"]

    if sim_path == "A":
        params = [{
            "blockStateCalls": [{"calls": [tx_obj]}],
            "traceTransfers": True,
            "validation": False,
            "returnFullTransactions": False
        }, block_param]
        
        try:
            res = await rpc.call("eth_simulateV1", params, cu_cost=250, priority=priority)
            call_res = res[0]["calls"][0]
            
            status_hex = call_res.get("status", "0x0")
            status = "success" if status_hex == "0x1" else "reverted"
            
            return SimResult(
                path="A",
                status=status,
                gas_used=int(call_res.get("gasUsed", "0x0"), 16),
                return_data=call_res.get("returnData"),
                revert_reason=call_res.get("error"),
                logs=call_res.get("logs", []),
                effects_source="simulation"
            )
        except Exception as e:
            return SimResult(
                path="A",
                status="error",
                revert_reason=str(e),
                logs=[],
                effects_source="simulation"
            )
            
    return SimResult(
        path="C",
        status="unsupported",
        logs=[],
        effects_source="abi_semantics"
    )
