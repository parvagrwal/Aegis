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
