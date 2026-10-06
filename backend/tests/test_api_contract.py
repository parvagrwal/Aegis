from fastapi.testclient import TestClient
from aegis.main import app
from aegis.models.api import Health, CaseResponse

client = TestClient(app)

def test_api_health():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    Health(**response.json())

def test_api_case():
    response = client.get("/api/v1/cases/123")
    assert response.status_code == 200
    CaseResponse(**response.json())
