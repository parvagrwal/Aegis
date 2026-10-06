from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Aegis API")

class Health(BaseModel):
    status: str

@app.get("/api/v1/health", response_model=Health)
async def health_check():
    return Health(status="ok")
