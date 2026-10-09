import os
import json
import httpx

class Narrator:
    async def explain(self, features: list, prompt: str = "") -> str:
        output = await self._call_llm(features, prompt)
        if "<script>" in output or "adversarial" in output:
            return self._fallback_template(features)
        return output
        
    async def _call_llm(self, features, prompt):
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            return self._fallback_template(features)
        payload = {
            "model": "llama-3.1-70b-versatile",
            "messages": [
                {"role": "system", "content": "You are Aegis Narrator. Explain these blockchain features in simple English."},
                {"role": "user", "content": f"Prompt: {prompt}
Features: {json.dumps(features)}"}
            ]
        }
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post("https://api.groq.com/openai/v1/chat/completions", headers={"Authorization": f"Bearer {api_key}"}, json=payload, timeout=10.0)
                return resp.json()["choices"][0]["message"]["content"]
        except:
            return self._fallback_template(features)
            
    def _fallback_template(self, features):
        return "This transaction was flagged due to specific features matching our policy."