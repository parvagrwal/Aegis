import os
import httpx
import json

class TGClient:
    def __init__(self):
        self.host = os.environ.get("TG_HOST", "").rstrip("/")
        self.graph = os.environ.get("TG_GRAPH", "Aegis")
        self.secret = os.environ.get("TG_SECRET", "")
        
        # TigerGraph RESTPP runs on port 9000 by default. Cloud might proxy it via 443.
        # tgcloud REST endpoints are usually on 9000
        self.base_url = f"{self.host}:9000" if "tgcloud" in self.host and ":9000" not in self.host else self.host
        
        self.token = None
        self.client = httpx.AsyncClient(timeout=10.0)
        
        from aegis.graph.local_graph import LocalGraph
        self.fallback = LocalGraph()
        self.use_fallback = False
        self.failures = 0

    async def _get_token(self):
        if self.token: return self.token
        url = f"{self.base_url}/requesttoken"
        
        try:
            resp = await self.client.post(url, json={"secret": self.secret, "graph": self.graph})
            resp.raise_for_status()
            data = resp.json()
            if not data.get("error"):
                self.token = data.get("token")
        except Exception:
            pass
        return self.token

    async def run(self, query: str, params: dict, timeout_s: float = 1.5) -> list:
        if self.use_fallback:
            return await self.fallback.run(query, params, timeout_s)
            
        token = await self._get_token()
        url = f"{self.base_url}/query/{self.graph}/{query}"
        
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        try:
            resp = await self.client.get(url, params=params, headers=headers, timeout=timeout_s)
            resp.raise_for_status()
            data = resp.json()
            if not data.get("error"):
                return data.get("results", [])
        except Exception:
            return []
        return []

    async def upsert(self, data: dict):
        if self.use_fallback:
            return await self.fallback.upsert(data)
            
        token = await self._get_token()
        url = f"{self.base_url}/graph/{self.graph}"
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        
        try:
            resp = await self.client.post(url, json=data, headers=headers)
            resp.raise_for_status()
            self.failures = 0
            return resp.json()
        except Exception as e:
            self.failures += 1
            if self.failures >= 3:
                self.use_fallback = True
            return {"error": True, "message": str(e)}

    async def keepalive(self) -> bool:
        if self.use_fallback:
            return await self.fallback.keepalive()
            
        try:
            res = await self.run("echo_alive", {})
            self.failures = 0
            return True
        except Exception:
            self.failures += 1
            if self.failures >= 3:
                self.use_fallback = True
            return False

    async def close(self):
        if self.use_fallback:
            await self.fallback.close()
        await self.client.aclose()
