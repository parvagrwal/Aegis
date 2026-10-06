import asyncio
from typing import Optional
from aegis.chain.rpc import RpcClient
from aegis.chain.explorer import ExplorerClient
from aegis.chain.bytecode import get_bytecode, is_sweeper

class Profile(dict):
    pass

async def get_profile(rpc: RpcClient, explorer: ExplorerClient, address: str, as_of_block: int | str = "latest") -> Profile:
    if not address or address == "0x" or address == "0x0000000000000000000000000000000000000000":
        return Profile({})
        
    code = await get_bytecode(rpc, address, as_of_block)
    kind = "contract" if code and len(code) > 2 else "eoa"
    
    verified = False
    creation = None
    first_funder = None
    age_days = -1.0
    
    if kind == "contract":
        # Check source verification
        src_info = await explorer.get_source(1, address) # assuming chain_id 1
        verified = src_info.get("verified", False)
        
        # Check creation block
        creations = await explorer.get_creation(1, [address])
        c_info = creations.get(address, {})
        tx_hash = c_info.get("tx_hash")
        
        if tx_hash:
            # get block from tx_hash if not provided by Etherscan V2
            block = c_info.get("block")
            if not block:
                try:
                    tx_rec = await rpc.call("eth_getTransactionByHash", [tx_hash])
                    if tx_rec and tx_rec.get("blockNumber"):
                        block = int(tx_rec["blockNumber"], 16)
                except Exception:
                    pass
            
            if block:
                current = as_of_block
                if isinstance(current, str):
                    try:
                        cur_block_obj = await rpc.call("eth_blockNumber", [])
                        current = int(cur_block_obj, 16)
                    except Exception:
                        current = block # fallback
                
                # age = blocks × 12 / 86400
                blocks = current - block
                if blocks > 0:
                    age_days = (blocks * 12) / 86400.0
                    
    # getAssetTransfers for first funder (if EOA or contract)
    try:
        block_param = hex(as_of_block) if isinstance(as_of_block, int) else "latest"
        params = [{
            "fromBlock": "0x0",
            "toBlock": block_param,
            "toAddress": address,
            "category": ["external", "internal"],
            "order": "asc",
            "maxCount": "0x1",
            "excludeZeroValue": True
        }]
        res = await rpc.call("alchemy_getAssetTransfers", params, cu_cost=150)
        transfers = res.get("transfers", [])
        if transfers:
            first_funder = transfers[0].get("from")
    except Exception:
        pass
        
    return Profile({
        "kind": kind,
        "verified": verified,
        "age_days": age_days,
        "first_funder": first_funder,
        "is_sweeper": is_sweeper(code) if kind == "contract" else False,
        "code_size": len(code) // 2 if code else 0
    })
