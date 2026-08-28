import pytest

from Models.Users import Users
from Repos.AccountsRepo import AccountsRepository
from Repos.BranchesRepo import BranchesRepository
from Repos.UsersRepo import UsersRepository
from Services.BranchesService import BranchesService
from Utilities.Status import UserRole


def make_user(role, user_id=1):
    return Users(user_id, "Test User", "test.user@example.com", role, branch_code="BR001")


def test_get_all_branches_allows_customer(monkeypatch):
    customer = make_user(UserRole.CUSTOMER)
    monkeypatch.setattr(BranchesRepository, "get_all_branches", staticmethod(lambda skip=0, limit=None, search=None: ["stub-branch"]))
    assert BranchesService.get_all_branches(customer) == ["stub-branch"]


def test_create_branch_rejects_manager():
    manager = make_user(UserRole.MANAGER)
    with pytest.raises(PermissionError):
        BranchesService.create_branch(manager, {"branch_code": "BR999", "location": "Test"})


def test_update_branch_rejects_staff():
    staff = make_user(UserRole.STAFF)
    with pytest.raises(PermissionError):
        BranchesService.update_branch(staff, "BR001", {"location": "New"})


def test_delete_branch_rejects_manager():
    manager = make_user(UserRole.MANAGER)
    with pytest.raises(PermissionError):
        BranchesService.delete_branch(manager, "BR001")


def test_delete_branch_cascades_accounts_and_clears_user_branch_codes(monkeypatch):
    admin = make_user(UserRole.ADMIN)
    calls = []
    monkeypatch.setattr(AccountsRepository, "delete_accounts_by_branch",
                         staticmethod(lambda branch_code: calls.append(("accounts", branch_code)) or 3))
    monkeypatch.setattr(UsersRepository, "clear_branch_code_by_branch",
                         staticmethod(lambda branch_code: calls.append(("users", branch_code)) or 2))
    monkeypatch.setattr(BranchesRepository, "delete_branch",
                         staticmethod(lambda branch_code: calls.append(("branch", branch_code)) or True))

    assert BranchesService.delete_branch(admin, "BR001") is True
    assert calls == [("accounts", "BR001"), ("users", "BR001"), ("branch", "BR001")]
