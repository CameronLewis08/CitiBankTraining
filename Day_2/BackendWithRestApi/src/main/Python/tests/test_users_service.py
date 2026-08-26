import pytest

from Models.Users import Users
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
