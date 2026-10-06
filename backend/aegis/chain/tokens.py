import asyncio
from cachetools import TTLCache
from aegis.chain.rpc import RpcClient
import eth_abi

cache = TTLCache(maxsize=1000, ttl=3600)

async def get_token_info(rpc: RpcClient, address: str) -> dict:
    if address in cache:
        return cache[address]
        
    # symbol() selector: 0x95d89b41
    # decimals() selector: 0x313ce567
    reqs = [
        {"jsonrpc": "2.0", "method": "eth_call", "params": [{"to": address, "data": "0x95d89b41"}, "latest"], "id": 1},
        {"jsonrpc": "2.0", "method": "eth_call", "params": [{"to": address, "data": "0x313ce567"}, "latest"], "id": 2},
    ]
    
    try:
        results = await rpc.call_batch(reqs, cu_cost_total=52)
        sym_hex = results[0]
        dec_hex = results[1]
        
        symbol = "UNKNOWN"
        decimals = 18
        
        if sym_hex and sym_hex != "0x":
            try:
                # String return types are dynamic, but we just try standard abi decoding
                symbol = eth_abi.decode(["string"], bytes.fromhex(sym_hex[2:]))[0]
            except Exception:
                try:
                    # Sometimes it's bytes32
                    symbol = bytes.fromhex(sym_hex[2:]).decode('utf-8').strip('\x00')
                except Exception:
                    pass
                
        if dec_hex and dec_hex != "0x":
            decimals = int(dec_hex, 16)
            
        info = {"symbol": symbol, "decimals": decimals}
        cache[address] = info
        return info
    except Exception:
        return {"symbol": "UNKNOWN", "decimals": 18}
