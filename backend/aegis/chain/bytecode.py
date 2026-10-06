from aegis.chain.rpc import RpcClient

async def get_bytecode(rpc: RpcClient, address: str, block: str | int = "latest") -> str:
    block_param = hex(block) if isinstance(block, int) else block
    res = await rpc.call("eth_getCode", [address, block_param], cu_cost=24)
    return res

def is_sweeper(code: str) -> bool:
    if not code or code == "0x":
        return False
    if len(code) > 3000: # WETH is larger, sweepers are usually small
        return False
    
    clean_code = code.lower().replace("ffffffffffffffffffffffffffffffffffffffff", "")
    return "ff" in clean_code
