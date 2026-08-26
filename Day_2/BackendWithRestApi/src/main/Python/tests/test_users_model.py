import bcrypt
import pytest

from Models.Users import Users
from Utilities.Status import UserRole


def make_user(role, user_id=1, branch_code="BR001"):
    return Users(user_id, "Test User", "test.user@example.com", role, branch_code=branch_code)


def test_set_role_requires_admin():
    admin = make_user(UserRole.ADMIN, user_id=1)
    target = make_user(UserRole.STAFF, user_id=2)
    target.set_role(admin, UserRole.MANAGER)
    assert target.get_role() == UserRole.MANAGER


def test_set_role_rejects_non_admin():
    manager = make_user(UserRole.MANAGER, user_id=1)
    target = make_user(UserRole.STAFF, user_id=2)
    with pytest.raises(PermissionError):
        target.set_role(manager, UserRole.ADMIN)


def test_set_branch_code_rejects_customer():
    customer = make_user(UserRole.CUSTOMER, user_id=1)
    target = make_user(UserRole.STAFF, user_id=2)
    with pytest.raises(PermissionError):
        target.set_branch_code(customer, "BR002")


def test_set_branch_code_rejects_customer_on_self():
    customer = make_user(UserRole.CUSTOMER, user_id=1)
    with pytest.raises(PermissionError):
        customer.set_branch_code(customer, "BR999")


def test_set_branch_code_allows_staff():
    staff = make_user(UserRole.STAFF, user_id=1)
    target = make_user(UserRole.STAFF, user_id=2)
    target.set_branch_code(staff, "BR002")
    assert target.get_branch_code() == "BR002"


def test_verify_password_roundtrip():
    user = make_user(UserRole.CUSTOMER)
    password_hash = bcrypt.hashpw(b"Secret123", bcrypt.gensalt()).decode("utf-8")
    user.set_password_hash(password_hash)
    assert user.verify_password("Secret123") is True
    assert user.verify_password("wrong") is False


def test_invalid_email_rejected():
    with pytest.raises(ValueError):
        Users(1, "Test User", "not-an-email", UserRole.CUSTOMER)


def test_to_dict_shape():
    user = make_user(UserRole.MANAGER)
    data = user.to_dict()
    assert data["user_id"] == 1
    assert data["role"] == "Manager"
    assert data["branch_code"] == "BR001"
