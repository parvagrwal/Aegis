import os
import httpx
import json

class LLMRouter:
    def __init__(self):
        self.api_key = os.environ.get("GROQ_API_KEY")
        self.fast_model = "openai/gpt-oss-20b"
        self.strong_model = "openai/gpt-oss-120b"

    async def route_and_call(self, task_type: str, system_prompt: str, user_content: str, json_mode: bool = False):
        if not self.api_key:
            return None
            
        # Route by task complexity
        model = self.strong_model if task_type == "planning" else self.fast_model
        
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ]
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}
            
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                    json=payload,
                    timeout=10.0
                )
                data = resp.json()
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"LLM Router Error: {e}")
            return None
