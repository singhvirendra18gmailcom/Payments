# tests/test_health.py

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "app": "AI Payment Assistant"
    }


def test_ai_health():
    response = client.get("/ai/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "provider": "local",
        "available": True
    }
