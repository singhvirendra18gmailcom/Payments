
from fastapi.testclient import TestClient
from app.main import app
from tests.utils import login_test_user, register_test_user

client = TestClient(app)

def test_login():
    email = register_test_user(client)

    response = login_test_user(client, email)

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"
