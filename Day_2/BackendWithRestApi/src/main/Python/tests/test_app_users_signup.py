"""
HTTP-layer tests for public self-signup on POST /users: proves that
omitting requesting_user_id no longer requires an existing authenticated
user, and that the role is always forced to Customer regardless of what
the client sends. The Repo layer is monkeypatched to stay DB-free,
consistent with this repo's existing testing pattern.
"""

from fastapi.testclient import TestClient

from app import app
from Repos.UsersRepo import UsersRepository
from Models.Users import Users

client = TestClient(app)


def test_signup_without_requesting_user_id_succeeds_and_forces_customer_role(monkeypatch):
    monkeypatch.setattr(UsersRepository, "get_next_user_id", staticmethod(lambda: 1))

    def fake_create(user_data):
        return Users(user_data["user_id"], user_data["name"], user_data["email"], user_data["role"])

    monkeypatch.setattr(UsersRepository, "create_user", staticmethod(fake_create))

    response = client.post(
        "/users",
        json={"name": "New User", "email": "new.user@example.com", "role": "Admin", "password": "secret123"},
    )

    assert response.status_code == 200
    assert response.json()["role"] == "Customer"
