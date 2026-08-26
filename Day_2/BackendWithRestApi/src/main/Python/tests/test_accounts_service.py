import pytest

from Models.Accounts import CheckingAccount
from Models.Users import Users
from Repos.AccountsRepo import AccountsRepository
from Services.AccountsService import AccountsService
from Utilities.Status import AccountStatus, UserRole


def make_user(role, user_id=1):
    return Users(user_id, "Test User", "test.user@example.com", role, branch_code="BR001")


def test_create_account_rejects_customer():
    customer = make_user(UserRole.CUSTOMER)
    with pytest.raises(PermissionError):
        AccountsService.create_account(customer, {
            "account_id": "ACC-1", "owner_id": 1, "balance": 100.0,
            "branch_code": "BR001", "account_type": "Checking",
        })


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
