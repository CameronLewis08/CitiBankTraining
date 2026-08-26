"""
User Model for the Banking Domain REST API:
    Represents a user of any role (Admin/Manager/Staff/Customer). Ported
    from Day_1's console-app Users class, with email-based identity
    (Day_2's existing convention) instead of Day_1's username-based one.
"""

import bcrypt

from Utilities.Status import UserRole


class Users:
    def __init__(self, user_id, name, email, role, branch_code=None, password_hash=None):
        self.set_user_id(user_id)
        self.set_name(name)
        self.set_email(email)
        self.role = role if isinstance(role, UserRole) else UserRole(role)
        self.branch_code = branch_code
        self.password_hash = password_hash

    def get_user_id(self):
        return self.user_id

    def get_name(self):
        return self.name

    def get_email(self):
        return self.email

    def get_role(self):
        return self.role

    def get_branch_code(self):
        return self.branch_code

    def get_password_hash(self):
        return self.password_hash

    def set_user_id(self, user_id):
        if not user_id:
            raise ValueError("User ID cannot be empty.")
        self.user_id = user_id

    def set_name(self, name):
        if not name:
            raise ValueError("Name cannot be empty.")
        self.name = name

    def set_email(self, email):
        if not email or "@" not in email or "." not in email:
            raise ValueError("Invalid email format.")
        self.email = email

    def set_password_hash(self, password_hash):
        if not password_hash:
            raise ValueError("Password hash cannot be empty.")
        self.password_hash = password_hash

    def set_role(self, staff, new_role):
        if staff.get_role() != UserRole.ADMIN:
            raise PermissionError("Only Admin users can change roles.")
        self.role = new_role if isinstance(new_role, UserRole) else UserRole(new_role)

    def set_branch_code(self, staff, new_branch_code):
        if staff.get_role() == UserRole.CUSTOMER:
            raise PermissionError("Only non-Customer users can change branch codes.")
        if not new_branch_code:
            raise ValueError("Branch code cannot be empty.")
        self.branch_code = new_branch_code

    def verify_password(self, plain_password):
        if not self.password_hash or not plain_password:
            return False
        return bcrypt.checkpw(plain_password.encode("utf-8"), self.password_hash.encode("utf-8"))

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "role": self.role.value,
            "branch_code": self.branch_code,
            "password_hash": self.password_hash,
        }

    def __repr__(self):
        return f"User ID: {self.user_id}, Name: {self.name}, Email: {self.email}, Role: {self.role.value}"
