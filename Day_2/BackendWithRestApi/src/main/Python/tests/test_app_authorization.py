"""
DB-free HTTP-layer authorization tests for the final whole-branch review
fix wave: prove that requesting_user_id can no longer be omitted on the
endpoints identified as authorization gaps. These only exercise FastAPI's
request validation (which runs before any Controller/Service/Repo code),
so no live Mongo connection is required - consistent with this repo's
existing DB-free testing pattern for the Service layer.

Note: app.py registers a custom RequestValidationError handler
(`handle_validation_error`) that returns status_code=400 instead of
FastAPI's default 422 for validation errors - these tests assert 400 to
match that actual, intentional app behavior.
"""

from fastapi.testclient import TestClient

from app import app

client = TestClient(app)


def test_deposit_without_requesting_user_id_is_rejected():
    response = client.post("/accounts/ACC-DOES-NOT-EXIST/deposit", json={"amount": 100})
    assert response.status_code == 400


def test_update_user_without_requesting_user_id_is_rejected():
    response = client.put("/users/1", json={"name": "New Name"})
    assert response.status_code == 400


def test_get_accounts_requires_requesting_user_id():
    response = client.get("/accounts")
    assert response.status_code == 400


def test_get_user_by_id_requires_requesting_user_id():
    # Closes a user-enumeration gap: this route used to have no auth
    # requirement at all, so any user_id (a small sequential int) could be
    # scanned for a profile with no login. See UsersService.view_user_profile.
    response = client.get("/users/1")
    assert response.status_code == 400
