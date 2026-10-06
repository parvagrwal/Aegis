import asyncio

async def plan(sleep_time=0.0):
    await asyncio.sleep(sleep_time)
    return {"status": "decided"}
