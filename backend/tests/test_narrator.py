import pytest
from aegis.agent.narrator import Narrator

@pytest.mark.asyncio
async def test_narrator_fallback():
    n = Narrator()
    # Benign output
    out = await n.explain([], "This is a safe transfer.")
    assert out == "This is a safe transfer."
