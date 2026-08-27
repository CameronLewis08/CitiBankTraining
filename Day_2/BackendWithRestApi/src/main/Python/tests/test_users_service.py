import pytest

from Models.Users import Users
from Repos.UsersRepo import UsersRepository
from Services.UsersService import UsersService
from Utilities.Status import UserRole


def make_user(role, user_id=1):
    return Users(user_id, "Test User", "test.user@example.com", role, branch_code="BR001")


def test_create_user_rejects_staff():
    staff = make_user(UserRole.STAFF)
    with pytest.raises(PermissionError):
        UsersService.create_user(staff, {"user_id": 2, "name": "New", "email": "new@example.com", "role": "Customer"})


def test_create_user_rejects_customer():
    customer = make_user(UserRole.CUSTOMER)
    with pytest.raises(PermissionError):
        UsersService.create_user(customer, {"user_id": 2, "name": "New", "email": "new@example.com", "role": "Customer"})


def test_delete_user_rejects_staff():
    staff = make_user(UserRole.STAFF)
    with pytest.raises(PermissionError):
        UsersService.delete_user(staff, 2)


def test_delete_user_rejects_customer():
    customer = make_user(UserRole.CUSTOMER)
    with pytest.raises(PermissionError):
        UsersService.delete_user(customer, 2)


def test_search_users_by_branch_rejects_non_admin():
    manager = make_user(UserRole.MANAGER)
    with pytest.raises(PermissionError):
        UsersService.search_users_by_branch(manager, "BR001")


def test_search_users_by_branch_rejects_invalid_role():
    admin = make_user(UserRole.ADMIN)
    with pytest.raises(ValueError):
        UsersService.search_users_by_branch(admin, "BR001", role="Bogus")


def test_create_user_self_signup_forces_customer_role(monkeypatch):
    # Public self-signup: no requesting_user, so no permission check runs,
    # and any role the caller tried to sneak in gets overwritten.
    monkeypatch.setattr(UsersRepository, "get_next_user_id", staticmethod(lambda: 1))
    captured = {}

    def fake_create(user_data):
        captured["data"] = user_data
        return make_user(UserRole.CUSTOMER, user_id=user_data["user_id"])

    monkeypatch.setattr(UsersRepository, "create_user", staticmethod(fake_create))

    UsersService.create_user(None, {"name": "New", "email": "new@example.com", "role": "Admin"})

    assert captured["data"]["role"] == "Customer"


def test_create_user_self_signup_auto_assigns_user_id(monkeypatch):
    monkeypatch.setattr(UsersRepository, "get_next_user_id", staticmethod(lambda: 8))
    captured = {}

    def fake_create(user_data):
        captured["data"] = user_data
        return make_user(UserRole.CUSTOMER, user_id=user_data["user_id"])

    monkeypatch.setattr(UsersRepository, "create_user", staticmethod(fake_create))

    UsersService.create_user(None, {"name": "New", "email": "new@example.com"})

    assert captured["data"]["user_id"] == 8


def test_create_user_admin_can_still_choose_role_and_id(monkeypatch):
    admin = make_user(UserRole.ADMIN)
    captured = {}

    def fake_create(user_data):
        captured["data"] = user_data
        return make_user(UserRole.STAFF, user_id=user_data["user_id"])

    monkeypatch.setattr(UsersRepository, "create_user", staticmethod(fake_create))

    UsersService.create_user(admin, {"user_id": 42, "name": "New", "email": "new@example.com", "role": "Staff"})

    assert captured["data"]["user_id"] == 42
    assert captured["data"]["role"] == "Staff"


def test_search_users_by_branch_allows_admin_and_threads_filters(monkeypatch):
    # Repo call is stubbed so this stays DB-free regardless of environment
    # and verifies both that the Admin gate passes and that the resolved
    # role value and name filter are threaded through to the Repo call.
    admin = make_user(UserRole.ADMIN)
    captured = {}

    def fake_search(branch_code, role=None, name=None):
        captured["args"] = (branch_code, role, name)
        return []

    monkeypatch.setattr(UsersRepository, "search_users_by_branch", staticmethod(fake_search))
    result = UsersService.search_users_by_branch(admin, "BR001", role="Staff", name="Amy")
    assert result == []
    assert captured["args"] == ("BR001", "Staff", "Amy")
