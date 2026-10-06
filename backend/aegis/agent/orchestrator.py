import asyncio
import time

class Orchestrator:
    def __init__(self, timeout_s=4.1):
        self.timeout_s = timeout_s
        
    async def run(self, planner_task) -> dict:
        start_time = time.time()
        
        # We start the planner task
        task = asyncio.create_task(planner_task())
        
        try:
            # Wait for the planner to finish or timeout
            res = await asyncio.wait_for(asyncio.shield(task), timeout=self.timeout_s)
            res["version"] = "v2"
            return res
        except asyncio.TimeoutError:
            # The planner took too long, return v1 immediately.
            # The planner task continues running in the background.
            def background_cb(t):
                try:
                    res = t.result()
                    # In a real system, we'd emit v2 event here.
                    res["version"] = "v2"
                except Exception:
                    pass
            task.add_done_callback(background_cb)
            return {"status": "decided", "version": "v1"}
