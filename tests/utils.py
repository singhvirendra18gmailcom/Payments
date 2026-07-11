# tests/utils.py

import uuid


def register_test_user(client, password: str = "password123") -> str:
    email = f"{uuid.uuid4()}@test.com"

    response = client.post(
        "/auth/register",
        json={
            "name": "Test User",
            "email": email,
            "password": password
        }
    )
    assert response.status_code == 200

    return email


def login_test_user(client, email: str, password: str = "password123"):
    return client.post(
        "/auth/login",
        data={
            "username": email,
            "password": password
        }
    )


def get_auth_headers(client):
    email = register_test_user(client)
    response = login_test_user(client, email)
    assert response.status_code == 200

    token = response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }
