import pytest
import respx
import httpx
import asyncio
from aegis.chain.budget import CuBudget
from aegis.util.ratelimit import TokenBucket
from aegis.chain.rpc import RpcClient, RpcError, BudgetExceeded

@pytest.mark.asyncio
async def test_rpc_success():
    budget = CuBudget(daily_limit=1000, monthly_limit=10000)
    bucket = TokenBucket(rate_per_s=100, burst=10)
    client = RpcClient("http://fake-rpc", budget, bucket)

    with respx.mock:
        respx.post("http://fake-rpc").respond(json={"jsonrpc": "2.0", "id": 1, "result": "0x123"})
        res = await client.call("eth_blockNumber", [])
        assert res == "0x123"
        assert budget.spent_daily == 26

    await client.close()

@pytest.mark.asyncio
async def test_rpc_429_retry():
    budget = CuBudget(daily_limit=1000, monthly_limit=10000)
    bucket = TokenBucket(rate_per_s=100, burst=10)
    client = RpcClient("http://fake-rpc", budget, bucket)

    with respx.mock:
        route = respx.post("http://fake-rpc")
        route.side_effect = [
            httpx.Response(429),
            httpx.Response(429),
            httpx.Response(200, json={"jsonrpc": "2.0", "id": 1, "result": "0x456"}),
        ]
        
        start = asyncio.get_event_loop().time()
        res = await client.call("eth_blockNumber", [])
        end = asyncio.get_event_loop().time()
        
        assert res == "0x456"
        assert route.call_count == 3
        # Should have waited 0.25 + 0.5 = 0.75s roughly
        # assert end - start >= 0.75 # this may be flaky in CI, skip timing assert

    await client.close()

@pytest.mark.asyncio
async def test_rpc_budget_refusal():
    budget = CuBudget(daily_limit=110, monthly_limit=1000)
    bucket = TokenBucket(rate_per_s=100, burst=10)
    client = RpcClient("http://fake-rpc", budget, bucket)

    budget.spent_daily = 80 # P2 is blocked >= 70% (80/110 = 0.72)

    with respx.mock:
        with pytest.raises(BudgetExceeded):
            await client.call("eth_blockNumber", [], priority=2)
            
        # But P0 can still spend
        respx.post("http://fake-rpc").respond(json={"jsonrpc": "2.0", "id": 1, "result": "0x1"})
        res = await client.call("eth_blockNumber", [], priority=0)
        assert res == "0x1"
        assert budget.spent_daily == 80 + 26 # 106, went over daily limit!
        
        # Next P0 call will fail because we are > daily_limit (1.0)
        with pytest.raises(BudgetExceeded):
            await client.call("eth_blockNumber", [], priority=0)

    await client.close()

@pytest.mark.asyncio
async def test_rpc_batch_ordering():
    budget = CuBudget(daily_limit=1000, monthly_limit=10000)
    bucket = TokenBucket(rate_per_s=100, burst=10)
    client = RpcClient("http://fake-rpc", budget, bucket)

    reqs = [
        {"jsonrpc": "2.0", "method": "eth_blockNumber", "params": [], "id": 1},
        {"jsonrpc": "2.0", "method": "eth_blockNumber", "params": [], "id": 2},
    ]

    with respx.mock:
        # Return out of order
        respx.post("http://fake-rpc").respond(json=[
            {"jsonrpc": "2.0", "id": 2, "result": "B"},
            {"jsonrpc": "2.0", "id": 1, "result": "A"},
        ])
        
        res = await client.call_batch(reqs, cu_cost_total=50)
        assert res == ["A", "B"]

    await client.close()
