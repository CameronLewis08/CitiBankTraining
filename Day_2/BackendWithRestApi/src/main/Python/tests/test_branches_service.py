import pytest

from Models.Users import Users
from Services.BranchesService import BranchesService
from Utilities.Status import UserRole


def make_user(role, user_id=1):
    return Users(user_id, "Test User", "test.user@example.com", role, branch_code="BR001")


def test_get_all_branches_rejects_customer():
    customer = make_user(UserRole.CUSTOMER)
    with pytest.raises(PermissionError):
        BranchesService.get_all_branches(customer)


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
