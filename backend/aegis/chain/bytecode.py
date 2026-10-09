from aegis.chain.rpc import RpcClient

async def get_bytecode(rpc: RpcClient, address: str, block: str | int = "latest") -> str:
    block_param = hex(block) if isinstance(block, int) else block
    res = await rpc.call("eth_getCode", [address, block_param], cu_cost=24)
    return res

def is_sweeper(code: str) -> bool:
    if not code or code == "0x":
        return False
    if len(code) > 3000:
        return False
    # Check for CALLER SELFDESTRUCT (33ff) or ADDRESS SELFDESTRUCT (30ff)
    clean_code = code.lower()
    return "33ff" in clean_code or "30ff" in clean_code