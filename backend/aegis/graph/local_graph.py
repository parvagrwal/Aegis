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
            tx_hash = params.get("tx_hash", "unknown")
            attacker = params.get("attacker", "unknown_attacker")
            # Return a deterministic 2-hop trace output
            return [{
                "path": f"{attacker[:8]}... -> 0xMixer... -> 0xExchange...",
                "hops": 2,
                "amount_usd": 1500000.0,
                "confidence": "high"
            }]
        elif query == "infra_anchors":
            return []
        return []

    async def keepalive(self) -> bool:
        return True

    async def close(self):
        pass
