import os
import json
from aegis.agent.llm_router import LLMRouter

class Narrator:
    async def explain(self, features: list, prompt: str = "") -> str:
        output = await self._call_llm(features, prompt)
        if not output or "<script>" in output or "adversarial" in output:
            return self._fallback_template(features)
        return output
        
    async def _call_llm(self, features, prompt):
        router = LLMRouter()
        system = "You are Aegis Narrator, an elite blockchain security assistant. You are given a JSON dump of a blockchain transaction analysis. Use this data to directly answer the users questions about how the hack occurred, what addresses were involved, and why it was flagged. Be highly specific using the data provided. IMPORTANT: At the very end of your response, add a new line starting with VOICE_SUMMARY: followed by a 2-3 crisp sentence conversational summary in simple relevant English."
        user = f"Prompt: {prompt}\nFeatures: {json.dumps(features)}"
        return await router.route_and_call("classification", system, user)
            
    def _fallback_template(self, features):
        return "This transaction was flagged due to specific features matching our policy."