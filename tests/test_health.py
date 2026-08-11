# tests/test_health.py

from fastapi.testclient import TestClient
from app.main import app

from unittest.mock import patch

client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "app": "AI Payment Assistant"
    }





@patch(
    "app.services.gemini_service.GeminiService.health_check",
    return_value=True,
)
def test_ai_health(mock_health_check):
    response = client.get("/ai/health")

    assert response.status_code == 200
    mock_health_check.assert_called_once()