import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from aegis.models.api import Health, CaseResponse

app = FastAPI(title="Aegis API")

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
    return AskResponse(
        answer=f"The answer to '{req.question}' is based on the record.",
        citations=["record.json:L10"]
    )
# Live deterministic scan (real pipeline) — vault frontend
from aegis.api.routes_scan import router as scan_router
app.include_router(scan_router)