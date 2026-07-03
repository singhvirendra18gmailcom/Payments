# tests/test_auth.py

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

import pytest
from app.database import SessionLocal
from app.models import User


@pytest.fixture
def cleanup_users():

    db = SessionLocal()

    db.query(User).delete()

    db.commit()
    db.close()

def test_register_user(cleanup_users):

    response = client.post(
        "/auth/register",
        json={
            "name": "Viren",
            "email": "virendra@test.com",
            "password": "password123"
        }
    )

    assert response.status_code == 200
