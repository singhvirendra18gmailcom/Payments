
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_login():

    response = client.post(
        "/auth/login",
        json={
            "email": "virendra@test.com",
            "password": "password123"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"