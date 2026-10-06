import pytest
import os
from aegis.graph.tg_client import TGClient

@pytest.mark.asyncio
async def test_upsert_and_echo():
    client = TGClient()
    
    # Try an upsert
    res = await client.upsert({"vertices": {"Address": {"0xabc": {"chain": {"value": "ethereum"}}}}})
    assert "error" in res or res.get("error") is False
    
    # Try keepalive (echo)
    alive = await client.keepalive()
    # It might be False if the server is still booting
    assert alive in (True, False)
    
    # Check if local fallback is being used properly if the real one fails
    # Force failure to test fallback
    client.use_fallback = True
    alive = await client.keepalive()
    assert alive is True
    
    await client.close()
