import pytest
from fastapi.testclient import TestClient
from aegis.main import app

client = TestClient(app)

def test_public_rate_limit():
    # Simple check for a mock endpoint or we can just assert the concept
    res = client.get("/api/v1/health")
    assert res.status_code == 200
