# tests/utils.py

import uuid


def get_auth_headers(client):

    email = f"{uuid.uuid4()}@test.com"

    client.post(
        "/auth/register",
        json={
            "name": "Test User",
            "email": email,
            "password": "password123"
        }
    )

    response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "password123"
        }
    )

    token = response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }