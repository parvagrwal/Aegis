from aegis.graph.tg_client import TGClient

async def fund_trace(client: TGClient, address: str, max_hops: int = 3) -> list:
    """
    Find paths from mixing services/OFAC addresses to the given address.
    """
    res = await client.run("fund_trace", {"target": address, "max_hops": max_hops})
    return res

async def infra_anchors(client: TGClient, address: str) -> list:
    """
    Find infrastructure anchors (shared code, shared deployer, etc).
    """
    res = await client.run("infra_anchors", {"target": address})
    return res
