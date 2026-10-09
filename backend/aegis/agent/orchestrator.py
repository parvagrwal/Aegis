import asyncio
from aegis.agent.planner import plan
from aegis.defend.executor import Executor
from aegis.defend.queue import DefendQueue
from aegis.agent.memory import Memory
import uuid

class Orchestrator:
    def __init__(self, timeout_s=10.0):
        self.timeout_s = timeout_s
        self.queue = DefendQueue()
        self.executor = Executor(self.queue)
        self.memory = Memory()
        
    async def run(self, event_context: dict) -> dict:
        attempt = 0
        max_attempts = 2
        done = False
        final_result = {"status": "success", "executed_actions": []}
        
        while not done and attempt < max_attempts:
            # Perceive
            observation = event_context
            
            # Plan
            plan_result = await plan(observation)
            actions = plan_result.get("actions", [])
            
            if not actions:
                done = True
                break
                
            # Act
            for action in actions:
                action_id = str(uuid.uuid4())
                self.queue.add(action_id, action)
                self.queue.set_status(action_id, "approved")
                
                try:
                    res = self.executor.execute(action_id)
                    final_result["executed_actions"].append(action)
                    
                    # Remember
                    self.memory.add_anchor(event_context.get("tx_hash", "unknown"), {"action": action, "result": res})
                    
                    if res.get("success"):
                        done = True
                except Exception as e:
                    print(f"Executor failed: {e}")
                    
            attempt += 1
            
        return final_result