import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from aegis.models.api import Health, CaseResponse

app = FastAPI(title="Aegis API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/v1/health", response_model=Health)
async def health_check():
    return Health(status="ok", lag_s=5)

@app.get("/api/v1/cases/{case_id}", response_model=CaseResponse)
async def get_case(case_id: str):
    return CaseResponse(
        id=case_id,
        verdict="malicious",
        risk="HIGH",
        features=["sim.approval_unlimited_to_eoa"],
        explanation="Flagged"
    )

from aegis.models.ask import AskRequest, AskResponse

@app.post("/api/v1/cases/{case_id}/ask", response_model=AskResponse)
async def ask_case(case_id: str, req: AskRequest):
    import os, httpx, json
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return AskResponse(answer="LLM not configured (missing GROQ_API_KEY).", citations=[])
    
    try:
        model = os.environ.get("GROQ_MODEL", "openai/gpt-oss-120b")
        url = "https://api.groq.com/openai/v1/chat/completions"
        
        # Build prompt using the passed context
        import json
        ctx_str = json.dumps(req.context, indent=2) if req.context else f"Incident {case_id}"
        
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are Aegis AI, an elite blockchain security assistant. You are given a JSON dump of a blockchain transaction analysis (features extracted, risk score, labels, verdicts). Use this data to directly answer the user's questions about how the hack occurred, what addresses were involved, and why it was flagged. Be highly specific using the data provided."},
                {"role": "user", "content": "Context:\\n" + ctx_str + "\\n\\nQuestion: " + req.question + "\\n\\nExplain this based purely on the provided context."}
            ]
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        async with httpx.AsyncClient() as client:
            r = await client.post(url, json=payload, headers=headers, timeout=25.0)
            r.raise_for_status()
            data = r.json()
            answer_text = data["choices"][0]["message"]["content"]
    except Exception as e:
        answer_text = f"LLM Error: {str(e)}"

    return AskResponse(
        answer=answer_text,
        citations=[f"case_{case_id}"]
    )
# Live deterministic scan (real pipeline) — vault frontend
from aegis.api.routes_scan import router as scan_router
app.include_router(scan_router)