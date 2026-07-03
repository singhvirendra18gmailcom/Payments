# tests/test_payment.py

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


from tests.utils import get_auth_headers


def test_mt103_chat():

    headers = get_auth_headers(client)

    response = client.post(
        "/chat/ask",
        headers=headers,
        json={
             "question": "MT103 seems to be mostly used"
        }
    )

    assert response.status_code == 200

    assert response.json() == {
    "question": "MT103 seems to be mostly used",
    "answer": "MT103 is used for international customer credit transfers over SWIFT."
    }

