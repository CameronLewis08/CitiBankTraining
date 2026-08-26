"""
Branch Model for the Banking Domain REST API:
    Ported from Day_1's console-app Branches class. Accounts are NOT
    embedded here (unlike Day_1) - they live in their own MongoDB
    collection with a branch_code field pointing back to a branch.
"""

from Utilities.Status import UserRole


class Branches:
    def __init__(self, branch_code, location, manager_id=None, staff_list=None):
        self.branch_code = branch_code
        self.location = location
        self.manager_id = manager_id
        self.staff_list = staff_list if staff_list is not None else []

    def get_branch_code(self):
        return self.branch_code

    def get_location(self):
        return self.location

    def get_manager_id(self, staff):
        if staff.get_role() == UserRole.CUSTOMER:
            raise PermissionError("Only staff can view the branch manager.")
        return self.manager_id

    def get_staff_list(self, staff):
        if staff.get_role() == UserRole.CUSTOMER:
            raise PermissionError("Only staff can view the branch staff list.")
        return self.staff_list

    def add_staff(self, user_id):
        if user_id not in self.staff_list:
            self.staff_list.append(user_id)

    def remove_staff(self, user_id):
        if user_id in self.staff_list:
            self.staff_list.remove(user_id)

    def set_manager(self, staff, manager_id):
        if staff.get_role() not in (UserRole.ADMIN, UserRole.MANAGER):
            raise PermissionError("Only Admins or Managers can assign a branch manager.")
        self.manager_id = manager_id

    def set_location(self, staff, new_location):
        if staff.get_role() != UserRole.ADMIN:
            raise PermissionError("Only Admins can change the branch location.")
        if not new_location:
            raise ValueError("Location cannot be empty.")
        self.location = new_location

    def to_dict(self):
        return {
            "branch_code": self.branch_code,
            "location": self.location,
            "manager_id": self.manager_id,
            "staff_list": self.staff_list,
        }

    def __repr__(self):
        return (f"Branch Code: {self.branch_code}, Location: {self.location}, "
                f"Manager ID: {self.manager_id}, Staff List: {self.staff_list}")
