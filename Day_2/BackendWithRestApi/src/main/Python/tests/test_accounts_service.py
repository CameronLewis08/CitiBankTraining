import re

import pytest

from Models.Accounts import CheckingAccount
from Models.Users import Users
from Repos.AccountsRepo import AccountsRepository
from Services.AccountsService import AccountsService
from Utilities.Status import AccountStatus, UserRole


def make_user(role, user_id=1):
    return Users(user_id, "Test User", "test.user@example.com", role, branch_code="BR001")


def test_create_account_allows_customer_to_open_for_self(monkeypatch):
    customer = make_user(UserRole.CUSTOMER, user_id=7)
    captured = {}

    def fake_create_account(account_data):
        captured["data"] = account_data
        return "created"

    monkeypatch.setattr(AccountsRepository, "get_account_by_id", staticmethod(lambda account_id, owner_id=None: None))
    monkeypatch.setattr(AccountsRepository, "create_account", staticmethod(fake_create_account))

    result = AccountsService.create_account(customer, {
        "balance": 100.0, "branch_code": "BR001", "account_type": "Checking",
    })

    assert result == "created"
    assert captured["data"]["owner_id"] == 7


def test_create_account_forces_owner_id_to_self_for_customer_even_if_spoofed(monkeypatch):
    customer = make_user(UserRole.CUSTOMER, user_id=7)
    captured = {}

    def fake_create_account(account_data):
        captured["data"] = account_data
        return "created"

    monkeypatch.setattr(AccountsRepository, "get_account_by_id", staticmethod(lambda account_id, owner_id=None: None))
    monkeypatch.setattr(AccountsRepository, "create_account", staticmethod(fake_create_account))

    AccountsService.create_account(customer, {
        "owner_id": 999, "balance": 100.0, "branch_code": "BR001", "account_type": "Checking",
    })

    assert captured["data"]["owner_id"] == 7


def test_create_account_generates_hashed_account_id_when_missing(monkeypatch):
    customer = make_user(UserRole.CUSTOMER, user_id=7)
    captured = {}

    def fake_create_account(account_data):
        captured["data"] = account_data
        return "created"

    monkeypatch.setattr(AccountsRepository, "get_account_by_id", staticmethod(lambda account_id, owner_id=None: None))
    monkeypatch.setattr(AccountsRepository, "create_account", staticmethod(fake_create_account))

    AccountsService.create_account(customer, {
        "balance": 100.0, "branch_code": "BR001", "account_type": "Checking",
    })

    assert re.fullmatch(r"ACC-[0-9a-f]{8}", captured["data"]["account_id"])


def test_create_account_keeps_provided_account_id_for_staff(monkeypatch):
    staff = make_user(UserRole.STAFF, user_id=2)
    captured = {}

    def fake_create_account(account_data):
        captured["data"] = account_data
        return "created"

    monkeypatch.setattr(AccountsRepository, "create_account", staticmethod(fake_create_account))

    AccountsService.create_account(staff, {
        "account_id": "ACC-1", "owner_id": 55, "balance": 100.0,
        "branch_code": "BR001", "account_type": "Checking",
    })

    assert captured["data"]["account_id"] == "ACC-1"
    assert captured["data"]["owner_id"] == 55


def test_delete_account_rejects_customer():
    customer = make_user(UserRole.CUSTOMER)
    with pytest.raises(PermissionError):
        AccountsService.delete_account(customer, "ACC-1")


def test_set_status_rejects_customer():
    customer = make_user(UserRole.CUSTOMER)
    with pytest.raises(PermissionError):
        AccountsService.set_status(customer, "ACC-1", AccountStatus.INACTIVE)


def test_set_status_allows_staff_to_reach_repo_layer():
    # Staff passes the permission gate; it will only fail later once it
    # tries to reach a real Mongo connection, proving the gate itself did
    # not block a legitimate role.
    staff = make_user(UserRole.STAFF)
    with pytest.raises(Exception) as exc_info:
        AccountsService.set_status(staff, "ACC-DOES-NOT-EXIST", AccountStatus.INACTIVE)
    assert not isinstance(exc_info.value, PermissionError)


def test_get_account_by_id_rejects_staff_from_other_branch(monkeypatch):
    # A Staff member's own branch_code differs from the target account's
    # branch_code -> PermissionError, proving cross-branch account reads
    # are blocked (mirrors the branch check in get_all_accounts). The Repo
    # lookup itself is stubbed so this stays DB-free and exercises only the
    # Service-layer branch comparison.
    staff = make_user(UserRole.STAFF)  # branch_code="BR001"
    other_branch_account = CheckingAccount("ACC-9001", 42, 100.0, "BR002")
    monkeypatch.setattr(
        AccountsRepository, "get_account_by_id",
        staticmethod(lambda account_id, owner_id=None: other_branch_account),
    )
    with pytest.raises(PermissionError):
        AccountsService.get_account_by_id(staff, "ACC-9001")


def test_transfer_funds_allows_staff_to_bypass_ownership_check():
    # Staff passes the role check and reaches the Repo layer unscoped by
    # ownership; it will only fail once it tries to reach a real Mongo
    # connection (or hits a nonexistent account), proving the bypass
    # branch is reachable and doesn't itself raise PermissionError.
    staff = make_user(UserRole.STAFF)
    with pytest.raises(Exception) as exc_info:
        AccountsService.transfer_funds(staff, "ACC-DOES-NOT-EXIST-A", "ACC-DOES-NOT-EXIST-B", 10.0)
    assert not isinstance(exc_info.value, PermissionError)


def test_search_accounts_by_branch_rejects_non_admin():
    staff = make_user(UserRole.STAFF)
    with pytest.raises(PermissionError):
        AccountsService.search_accounts_by_branch(staff, "BR001")


def test_search_accounts_by_branch_rejects_invalid_account_type():
    admin = make_user(UserRole.ADMIN)
    with pytest.raises(ValueError):
        AccountsService.search_accounts_by_branch(admin, "BR001", account_type="Bogus")


def test_search_accounts_by_branch_rejects_invalid_status():
    admin = make_user(UserRole.ADMIN)
    with pytest.raises(ValueError):
        AccountsService.search_accounts_by_branch(admin, "BR001", status="Bogus")


def test_search_accounts_by_branch_allows_admin_and_threads_filters(monkeypatch):
    # Repo call is stubbed so this stays DB-free regardless of environment
    # and verifies both that the Admin gate passes and that the resolved
    # enum values are threaded through to the Repo call correctly.
    admin = make_user(UserRole.ADMIN)
    captured = {}

    def fake_search(branch_code, account_type=None, status=None):
        captured["args"] = (branch_code, account_type, status)
        return []

    monkeypatch.setattr(AccountsRepository, "search_accounts_by_branch", staticmethod(fake_search))
    result = AccountsService.search_accounts_by_branch(admin, "BR001", account_type="Checking", status="active")
    assert result == []
    assert captured["args"] == ("BR001", "Checking", "active")
