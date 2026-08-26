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
