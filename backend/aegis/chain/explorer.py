import asyncio
import httpx
from typing import Optional
import os

class ExplorerClient:
    def __init__(self):
        self.api_key = os.environ.get("ETHERSCAN_API_KEY", "")
        self.client = httpx.AsyncClient()
        
    async def get_source(self, chain_id: int, address: str) -> dict:
        url = f"https://api.etherscan.io/v2/api?chainid={chain_id}&module=contract&action=getsourcecode&address={address}&apikey={self.api_key}"
        
        for attempt in range(2):
            try:
                resp = await self.client.get(url, timeout=10.0)
                resp.raise_for_status()
                data = resp.json()
                
                if data.get("status") == "0" and "rate limit" in data.get("message", "").lower():
                    await asyncio.sleep(1.0)
                    continue
                    
                if data.get("status") == "1" and data.get("result"):
                    res = data["result"][0]
                    verified = bool(res.get("SourceCode", ""))
                    contract_name = res.get("ContractName") if verified else None
                    proxy = (res.get("Proxy") == "1")
                    implementation = res.get("Implementation") if proxy else None
                    
                    return {
                        "verified": verified,
                        "contract_name": contract_name,
                        "proxy": proxy,
                        "implementation": implementation
                    }
                    
                # If we get here and it's not rate limit but status is 0, it might be unverified
                return {"verified": False, "contract_name": None, "proxy": False, "implementation": None}
                
            except Exception:
                if attempt == 0:
                    await asyncio.sleep(1.0)
                pass
                
        # Fallback to Blockscout if both fail
        fallback_url = "https://eth.blockscout.com/api" if chain_id == 1 else "https://eth-sepolia.blockscout.com/api"
        fb_url = f"{fallback_url}?module=contract&action=getsourcecode&address={address}"
        try:
            resp = await self.client.get(fb_url, timeout=10.0)
            resp.raise_for_status()
            data = resp.json()
            if data.get("status") == "1" and data.get("result"):
                res = data["result"][0]
                verified = bool(res.get("SourceCode", ""))
                return {
                    "verified": verified,
                    "contract_name": res.get("ContractName") if verified else None,
                    "proxy": False,
                    "implementation": None
                }
        except Exception:
            pass
            
        return {"verified": False, "contract_name": None, "proxy": False, "implementation": None}

    async def get_creation(self, chain_id: int, addresses: list[str]) -> dict[str, dict]:
        addrs_str = ",".join(addresses)
        url = f"https://api.etherscan.io/v2/api?chainid={chain_id}&module=contract&action=getcontractcreation&contractaddresses={addrs_str}&apikey={self.api_key}"
        
        for attempt in range(2):
            try:
                resp = await self.client.get(url, timeout=10.0)
                resp.raise_for_status()
                data = resp.json()
                
                if data.get("status") == "0" and "rate limit" in data.get("message", "").lower():
                    await asyncio.sleep(1.0)
                    continue
                    
                if data.get("status") == "1" and data.get("result"):
                    res = {}
                    for item in data["result"]:
                        res[item["contractAddress"]] = {
                            "creator": item.get("contractCreator"),
                            "tx_hash": item.get("txHash"),
                            "block": None # Etherscan V2 doesn't always return blockNumber here
                        }
                    return res
            except Exception:
                if attempt == 0:
                    await asyncio.sleep(1.0)
                pass
                
        return {}

    async def close(self):
        await self.client.aclose()
