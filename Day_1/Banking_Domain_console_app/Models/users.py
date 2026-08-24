"""
User Model for the Banking Domain Console Application:
    This module defines the User class, which represents a user in the banking domain. The User class contains attributes such as username, password, and account balance. It also includes methods for user authentication and account management.
    This module should be used in conjunction with other modules in the banking domain to provide a complete banking application experience.

"""

from enum import Enum

from status import OutcomeStatus, UserRole



class Users:
    def __init__(self, username, password, role, email, branch_code, account_list = None):
        self.username = username
        self._password = password
        self._role = role
        self.email = email
        self.branch_code = branch_code 
        self.account_list = account_list if account_list is not None else []
        

    def authenticate(self, username, password):
        if not username or not password:
            raise ValueError("Username and password cannot be empty.")
        else:
            return self.username == username and self._password == password

    def get_username(self):
        return self.username
    def get_password(self):
        return self._password
    def get_role(self):
        return self._role
    def get_email(self):
        return self.email
    def get_branch_code(self):
        return self.branch_code
    def get_account_list(self):
        return self.account_list

    

    def set_username(self, new_username):
        if not new_username:
            raise ValueError("Username cannot be empty.")
        else:
            self.username = new_username
            return f"{OutcomeStatus.SUCCESS.value}, Username updated to {new_username}."

    def set_password(self, new_password):
        if len(new_password) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        else:
            self._password = new_password
            return f"{OutcomeStatus.SUCCESS.value}, Password updated for user {self.username}."

    def set_role(self, staff, new_role):
        if staff.get_role() == UserRole.ADMIN:
            self._role = new_role
            return f"{OutcomeStatus.SUCCESS.value}, Role updated to {new_role.value} for user {self.username}."
        else:
            raise PermissionError("Only Admin users can change roles.")

    def set_email(self, new_email):
        if "@" not in new_email or "." not in new_email:
            raise ValueError("Invalid email format.")
        else:
            self.email = new_email
            return f"{OutcomeStatus.SUCCESS.value}, Email updated to {new_email} for user {self.username}."

    def set_branch_code(self, staff, new_branch_code):
        if staff.get_role() != UserRole.CUSTOMER:
            if not new_branch_code:
                raise ValueError("Branch code cannot be empty.")
            else:
                self.branch_code = new_branch_code
                return f"{OutcomeStatus.SUCCESS.value}, Branch code updated to {new_branch_code} for user {self.username}."    
        else:
            raise PermissionError("Only non-Customer users can change branch codes.")
        

    def __repr__(self):
        return f"Username: {self.username}, Password: {self._password}, Role: {self._role.value}"

