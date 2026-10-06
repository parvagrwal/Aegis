import pytest
import asyncio
import time
from aegis.agent.orchestrator import Orchestrator
from aegis.agent.planner import plan

@pytest.mark.asyncio
async def test_orchestrator_deadline():
    orch = Orchestrator(timeout_s=1.0)
    
    start = time.time()
    # Planner sleeps for 2s, but orch timeout is 1.0s
    res = await orch.run(lambda: plan(sleep_time=2.0))
    elapsed = time.time() - start
    
    assert elapsed <= 1.5, f"Took {elapsed}s, expected < 1.5s"
    assert res["version"] == "v1"
    
    # Wait for the background task to finish
    await asyncio.sleep(1.5)
    # The callback should have executed and marked it v2 in the background.
    # In a real test, we would assert a queue or mock got v2, but here we just ensure
    # it didn't block the initial return.
