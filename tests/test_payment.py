# tests/test_payment.py

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


from tests.utils import get_auth_headers


def test_mt103_explanation():

    headers = get_auth_headers(client)

    response = client.post(
        "/payments/explain",
        headers=headers,
        json={
            "message_type": "MT103",
            "content": "What is MT103?"
        }
    )

    assert response.status_code == 200

    assert response.status_code == 200

    data = response.json()

    assert data["message_type"] == "MT103"


def test_mt103_requires_authentication():

    response = client.post(
        "/payments/explain",
        json={
            "message_type": "MT103",
            "content": "What is MT103?"
        }
    )

    assert response.status_code == 401