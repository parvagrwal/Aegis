import asyncio
import os
import json
from aegis.agent.llm_router import LLMRouter

async def plan(context_data: dict = None):
    if not context_data or not os.environ.get("GROQ_API_KEY"):
        return {"status": "decided", "actions": []}
        
    prompt = 'You are Aegis Agent Planner. Given this JSON transaction context, output ONLY a JSON object with an "actions" key containing an array of required defense actions. For example: {"actions": [{"type": "REVOKE_APPROVAL", "spender": "0x...", "token": "0x...", "chain_id": 1}]}. If no defense is needed, output {"actions": []}.'
    
    router = LLMRouter()
    content = await router.route_and_call("planning", prompt, json.dumps(context_data)[:2000], json_mode=True)
    
    if content:
        try:
            actions = json.loads(content).get("actions", [])
            return {"status": "decided", "actions": actions}
        except:
            pass
            
    return {"status": "decided", "actions": []}