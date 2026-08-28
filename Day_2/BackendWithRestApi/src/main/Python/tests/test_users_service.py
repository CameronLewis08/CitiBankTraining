import pytest

from Models.Users import Users
from Repos.UsersRepo import UsersRepository
from Services.UsersService import UsersService
from Utilities.Status import UserRole


def make_user(role, user_id=1):
    return Users(user_id, "Test User", "test.user@example.com", role, branch_code="BR001")


def test_view_user_profile_allows_self(monkeypatch):
    customer = make_user(UserRole.CUSTOMER, user_id=6)
    monkeypatch.setattr(UsersRepository, "get_user_by_id", staticmethod(lambda target_id: customer))

    result = UsersService.view_user_profile(customer, 6)

    assert result is customer


def test_view_user_profile_rejects_customer_viewing_someone_else(monkeypatch):
    customer = make_user(UserRole.CUSTOMER, user_id=6)
    other = make_user(UserRole.CUSTOMER, user_id=7)
    monkeypatch.setattr(UsersRepository, "get_user_by_id", staticmethod(lambda target_id: other))

    with pytest.raises(PermissionError):
        UsersService.view_user_profile(customer, 7)


def test_view_user_profile_scopes_manager_and_staff_to_own_branch(monkeypatch):
    manager = make_user(UserRole.MANAGER, user_id=2)
    same_branch_user = Users(4, "Same Branch", "same@example.com", UserRole.STAFF, branch_code="BR001")
    monkeypatch.setattr(UsersRepository, "get_user_by_id", staticmethod(lambda target_id: same_branch_user))

    result = UsersService.view_user_profile(manager, 4)

    assert result is same_branch_user


def test_view_user_profile_rejects_manager_viewing_other_branch(monkeypatch):
    manager = make_user(UserRole.MANAGER, user_id=2)
    other_branch_user = Users(5, "Other Branch", "other@example.com", UserRole.STAFF, branch_code="BR002")
    monkeypatch.setattr(UsersRepository, "get_user_by_id", staticmethod(lambda target_id: other_branch_user))

    with pytest.raises(PermissionError):
        UsersService.view_user_profile(manager, 5)


def test_view_user_profile_allows_admin_to_view_anyone(monkeypatch):
    admin = make_user(UserRole.ADMIN, user_id=1)
    other_branch_user = Users(5, "Other Branch", "other@example.com", UserRole.STAFF, branch_code="BR002")
    monkeypatch.setattr(UsersRepository, "get_user_by_id", staticmethod(lambda target_id: other_branch_user))

    result = UsersService.view_user_profile(admin, 5)

    assert result is other_branch_user


def test_view_user_profile_returns_none_for_missing_user(monkeypatch):
    admin = make_user(UserRole.ADMIN, user_id=1)
    monkeypatch.setattr(UsersRepository, "get_user_by_id", staticmethod(lambda target_id: None))

    assert UsersService.view_user_profile(admin, 999) is None


def test_get_all_users_rejects_customer():
    customer = make_user(UserRole.CUSTOMER)
    with pytest.raises(PermissionError):
        UsersService.get_all_users(customer)


def test_get_all_users_scopes_manager_and_staff_to_own_branch(monkeypatch):
    manager = make_user(UserRole.MANAGER)
    captured = {}

    def fake_search(branch_code, role=None, name=None, skip=0, limit=None, search=None):
        captured["args"] = (branch_code, role, name)
        return []

    monkeypatch.setattr(UsersRepository, "search_users_by_branch", staticmethod(fake_search))

    UsersService.get_all_users(manager)

    assert captured["args"] == ("BR001", None, None)


def test_get_all_users_admin_sees_everyone(monkeypatch):
    admin = make_user(UserRole.ADMIN)
    monkeypatch.setattr(
        UsersRepository, "get_all_users",
        staticmethod(lambda skip=0, limit=None, search=None, role=None: ["all-users"]),
    )

    result = UsersService.get_all_users(admin)

    assert result == ["all-users"]


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


def test_update_user_rejects_manager_changing_own_branch():
    manager = make_user(UserRole.MANAGER, user_id=2)
    with pytest.raises(PermissionError):
        UsersService.update_user(manager, 2, {"branch_code": "BR002"})


def test_update_user_rejects_staff_changing_own_branch():
    staff = make_user(UserRole.STAFF, user_id=4)
    with pytest.raises(PermissionError):
        UsersService.update_user(staff, 4, {"branch_code": "BR002"})


def test_update_user_rejects_manager_changing_another_managers_branch():
    manager = make_user(UserRole.MANAGER, user_id=2)
    with pytest.raises(PermissionError):
        UsersService.update_user(manager, 3, {"branch_code": "BR002"})


def test_update_user_allows_admin_changing_managers_branch(monkeypatch):
    admin = make_user(UserRole.ADMIN, user_id=1)
    captured = {}

    def fake_update(user_id, user_data, requesting_user):
        captured["args"] = (user_id, user_data)
        return make_user(UserRole.MANAGER, user_id=user_id)

    monkeypatch.setattr(UsersRepository, "update_user", staticmethod(fake_update))

    UsersService.update_user(admin, 2, {"branch_code": "BR002"})

    assert captured["args"] == (2, {"branch_code": "BR002"})


def test_update_user_allows_admin_changing_own_branch(monkeypatch):
    admin = make_user(UserRole.ADMIN, user_id=1)
    captured = {}

    def fake_update(user_id, user_data, requesting_user):
        captured["args"] = (user_id, user_data)
        return admin

    monkeypatch.setattr(UsersRepository, "update_user", staticmethod(fake_update))

    UsersService.update_user(admin, 1, {"branch_code": "BR001"})

    assert captured["args"] == (1, {"branch_code": "BR001"})


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
