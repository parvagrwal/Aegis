import asyncio
import os
import json
import httpx

async def plan(context_data: dict = None, sleep_time=0.0):
    await asyncio.sleep(sleep_time)
    
    if not context_data:
        return {"status": "decided", "actions": []}
        
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return {"status": "decided", "actions": []}
        
    prompt = "You are Aegis Agent Planner. Given this JSON transaction context, output ONLY a JSON array of required defense actions. For example: [{"type": "REVOKE_APPROVAL", "spender": "0x...", "token": "0x...", "chain_id": 1}]. If no defense is needed, output []."
    
    payload = {
        "model": "llama-3.1-70b-versatile",
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": json.dumps(context_data)[:2000]}
        ],
        "response_format": {"type": "json_object"}
    }
    
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json=payload,
                timeout=10.0
            )
            data = resp.json()
            actions = json.loads(data["choices"][0]["message"]["content"]).get("actions", [])
            return {"status": "decided", "actions": actions}
    except Exception:
        pass
        
    return {"status": "decided", "actions": []}