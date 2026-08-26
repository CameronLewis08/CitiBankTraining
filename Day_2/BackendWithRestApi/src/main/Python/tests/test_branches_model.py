import pytest

from Models.Branches import Branches
from Models.Users import Users
from Utilities.Status import UserRole


def make_user(role, user_id=1):
    return Users(user_id, "Test User", "test.user@example.com", role, branch_code="BR001")


def test_get_manager_id_rejects_customer():
    branch = Branches("BR001", "Downtown", manager_id=2)
    customer = make_user(UserRole.CUSTOMER)
    with pytest.raises(PermissionError):
        branch.get_manager_id(customer)


def test_get_manager_id_allows_staff():
    branch = Branches("BR001", "Downtown", manager_id=2)
    staff = make_user(UserRole.STAFF)
    assert branch.get_manager_id(staff) == 2


def test_set_location_requires_admin():
    branch = Branches("BR001", "Downtown")
    manager = make_user(UserRole.MANAGER)
    with pytest.raises(PermissionError):
        branch.set_location(manager, "Uptown")


def test_set_location_allows_admin():
    branch = Branches("BR001", "Downtown")
    admin = make_user(UserRole.ADMIN)
    branch.set_location(admin, "Uptown")
    assert branch.get_location() == "Uptown"


def test_set_manager_rejects_staff():
    branch = Branches("BR001", "Downtown")
    staff = make_user(UserRole.STAFF)
    with pytest.raises(PermissionError):
        branch.set_manager(staff, 5)


def test_set_manager_allows_admin():
    branch = Branches("BR001", "Downtown")
    admin = make_user(UserRole.ADMIN)
    branch.set_manager(admin, 5)
    assert branch.manager_id == 5


def test_add_and_remove_staff():
    branch = Branches("BR001", "Downtown")
    branch.add_staff(9)
    assert 9 in branch.staff_list
    branch.remove_staff(9)
    assert 9 not in branch.staff_list


def test_to_dict_shape():
    branch = Branches("BR001", "Downtown", manager_id=2, staff_list=[3, 4])
    data = branch.to_dict()
    assert data == {"branch_code": "BR001", "location": "Downtown", "manager_id": 2, "staff_list": [3, 4]}
