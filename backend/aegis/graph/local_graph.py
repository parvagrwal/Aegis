class LocalGraph:
    def __init__(self):
        self.vertices = {}
        self.edges = {}
        
    async def upsert(self, data: dict):
        if "vertices" in data:
            for v_type, items in data["vertices"].items():
                if v_type not in self.vertices:
                    self.vertices[v_type] = {}
                for v_id, attrs in items.items():
                    self.vertices[v_type][v_id] = attrs
                    
        if "edges" in data:
            for source_type, sources in data["edges"].items():
                if source_type not in self.edges:
                    self.edges[source_type] = {}
                for source_id, edge_types in sources.items():
                    if source_id not in self.edges[source_type]:
                        self.edges[source_type][source_id] = {}
                    for e_type, targets in edge_types.items():
                        if e_type not in self.edges[source_type][source_id]:
                            self.edges[source_type][source_id][e_type] = {}
                        for target_type, t_items in targets.items():
                            if target_type not in self.edges[source_type][source_id][e_type]:
                                self.edges[source_type][source_id][e_type][target_type] = {}
                            for target_id, attrs in t_items.items():
                                self.edges[source_type][source_id][e_type][target_type][target_id] = attrs
        return {"error": False, "message": "success"}


    async def run(self, query: str, params: dict, timeout_s: float = 1.5) -> list:
        if query == "echo_alive":
            return [{"alive": True}]
        elif query == "fund_trace":
            import os, httpx, asyncio
            
            attacker = params.get("attacker")
            if not attacker or attacker == "unknown_attacker":
                return [{"status": "unavailable", "reason": "No valid attacker address provided"}]
                
            key = os.environ.get("ALCHEMY_API_KEY") or os.environ.get("NEXT_PUBLIC_ALCHEMY")
            if not key:
                return [{"status": "unavailable", "reason": "Missing ALCHEMY_API_KEY"}]
                
            url = f"https://eth-mainnet.g.alchemy.com/v2/{key}"
            
            async def get_transfers(address):
                payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "alchemy_getAssetTransfers",
                    "params": [{
                        "fromBlock": "0x0",
                        "toBlock": "latest",
                        "fromAddress": address,
                        "category": ["external", "erc20"],
                        "maxCount": "0x64",
                        "excludeZeroValue": True
                    }]
                }
                async with httpx.AsyncClient() as client:
                    resp = await client.post(url, json=payload, timeout=5.0)
                    resp.raise_for_status()
                    data = resp.json()
                    if "error" in data:
                        raise Exception(data["error"]["message"])
                    return data.get("result", {}).get("transfers", [])
                    
            try:
                # Hop 1
                transfers_1 = await get_transfers(attacker)
                if not transfers_1:
                    return [{"status": "unavailable", "reason": "No outgoing transfers found"}]
                    
                # Sort by value (handling None)
                def get_val(t):
                    try: return float(t.get("value") or 0)
                    except: return 0.0
                    
                transfers_1.sort(key=get_val, reverse=True)
                top_3 = transfers_1[:3]
                
                results = []
                for t1 in top_3:
                    hop1_to = t1.get("to")
                    hop1_val = get_val(t1)
                    hop1_asset = t1.get("asset") or "ETH"
                    
                    if not hop1_to: continue
                    
                    # Hop 2
                    try:
                        transfers_2 = await get_transfers(hop1_to)
                        transfers_2.sort(key=get_val, reverse=True)
                        if transfers_2:
                            t2 = transfers_2[0]
                            hop2_to = t2.get("to")
                            hop2_val = get_val(t2)
                            hop2_asset = t2.get("asset") or "ETH"
                            
                            results.append({
                                "path": f"{attacker} -> {hop1_to} ({hop1_val} {hop1_asset}) -> {hop2_to} ({hop2_val} {hop2_asset})",
                                "hops": 2,
                                "amount_usd": hop1_val, # Approx
                                "confidence": "high based on deterministic RPC trace"
                            })
                        else:
                            results.append({
                                "path": f"{attacker} -> {hop1_to} ({hop1_val} {hop1_asset}) -> End",
                                "hops": 1,
                                "amount_usd": hop1_val,
                                "confidence": "medium (no further hops)"
                            })
                    except Exception:
                        results.append({
                            "path": f"{attacker} -> {hop1_to} ({hop1_val} {hop1_asset}) -> Error",
                            "hops": 1,
                            "amount_usd": hop1_val,
                            "confidence": "low (RPC failed on hop 2)"
                        })
                        
                if not results:
                    return [{"status": "unavailable", "reason": "No valid targets found in top transfers"}]
                    
                return results
                
            except Exception as e:
                return [{"status": "unavailable", "reason": str(e)}]
                
        elif query == "infra_anchors":
            return []
        return []
    async def keepalive(self) -> bool:
        return True

    async def close(self):
        pass
