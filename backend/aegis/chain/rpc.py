import httpx
import asyncio
from typing import Any
from aegis.chain.budget import CuBudget
from aegis.util.ratelimit import TokenBucket

class RpcError(Exception):
    pass

class BudgetExceeded(Exception):
    pass

class RpcClient:
    def __init__(self, url: str, budget: CuBudget, bucket: TokenBucket):
        self.url = url
        self.budget = budget
        self.bucket = bucket
        self.client = httpx.AsyncClient()

    async def call(self, method: str, params: list, cu_cost: int = 26, priority: int = 0) -> Any:
        if not self.budget.can_spend(cu_cost, priority):
            raise BudgetExceeded("Budget exceeded for this priority level")

        self.budget.spend(cu_cost)

        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": 1
        }

        retries = [0.25, 0.5, 1.0]
        attempts = 0

        while True:
            await self.bucket.acquire(1)
            try:
                resp = await self.client.post(self.url, json=payload, timeout=10.0)
                if resp.status_code == 429:
                    if attempts < len(retries):
                        await asyncio.sleep(retries[attempts])
                        attempts += 1
                        continue
                    else:
                        raise RpcError("Rate limited: max retries exceeded")
                
                resp.raise_for_status()
                data = resp.json()
                if "error" in data:
                    raise RpcError(data["error"]["message"] if isinstance(data["error"], dict) else data["error"])
                return data["result"]
            except httpx.RequestError as e:
                raise RpcError(str(e))
                
    async def call_batch(self, reqs: list[dict], cu_cost_total: int, priority: int = 0) -> list[Any]:
        if not self.budget.can_spend(cu_cost_total, priority):
            raise BudgetExceeded("Budget exceeded for batch")
        
        self.budget.spend(cu_cost_total)
        
        retries = [0.25, 0.5, 1.0]
        attempts = 0

        while True:
            await self.bucket.acquire(1)
            try:
                resp = await self.client.post(self.url, json=reqs, timeout=10.0)
                if resp.status_code == 429:
                    if attempts < len(retries):
                        await asyncio.sleep(retries[attempts])
                        attempts += 1
                        continue
                    else:
                        raise RpcError("Rate limited: max retries exceeded")
                        
                resp.raise_for_status()
                data = resp.json()
                
                id_to_resp = {item.get("id"): item for item in data if isinstance(item, dict)}
                ordered = []
                for r in reqs:
                    ans = id_to_resp.get(r.get("id"))
                    if ans and "error" not in ans:
                        ordered.append(ans.get("result"))
                    else:
                        ordered.append(None)
                return ordered
            except httpx.RequestError as e:
                raise RpcError(str(e))

    async def close(self):
        await self.client.aclose()
