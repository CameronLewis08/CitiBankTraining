"""
Bank Model for the Banking Domain Console Application:
    This module defines the Bank class, which represents a bank in the banking domain. The Bank class contains attributes such as bank name, branch name, and a list of users associated with the bank. It also includes methods for managing users and performing banking operations.
    This module should be used in conjunction with other modules in the banking domain to provide a complete banking application experience.

"""

from users import Users, UserRole
from branches import Branches
from accounts import Accounts

class Banks:
    def __init__(self, bank_name, branch_codes=None, users=None):
        self.bank_name = bank_name
        self.branch_codes = branch_codes if branch_codes is not None else {}
        self.users = users if users is not None else {}

    def get_bank_name(self):
        return self.bank_name
    
    def get_branch_codes(self, user):
        if user._role != UserRole.CUSTOMER:
            raise PermissionError("Only Staff can view all branch codes.")
        else: return self.branch_codes
    
    def get_users(self, user):
        if user._role != UserRole.MANAGER or user._role != UserRole.ADMIN:
            raise PermissionError("Only Managers and Admins can view all users.")
        else: return self.users

    
    def create_branch(self, user, branch_code, location, manager_id, staff_list):
        if user._role != UserRole.ADMIN:
            raise PermissionError("Only Admins can create branches.")
        else:
            branch = Branches(branch_code, location, manager_id, staff_list)
            self.branch_codes[branch_code] = branch

            return f"Branch {branch_code} created at {location} with manager {manager_id}."
    
    def remove_branch(self, user, branch_code):
        if user._role != UserRole.ADMIN:
            raise PermissionError("Only Admins can remove branches.")
        else:
            if branch_code in self.branch_codes:
                del self.branch_codes[branch_code]
            else:
                raise ValueError(f"Branch code {branch_code} does not exist.")
            
        return f"Branch {branch_code} removed."

    def create_user(self, user, username, password, role, email, branch_code):
        if user._role != UserRole.CUSTOMER:
            raise PermissionError("Only staff can create users.")
        else:
            if branch_code not in self.branch_codes:
                raise ValueError(f"Branch code {branch_code} does not exist.")
            
            user = Users(username, password, role, email, branch_code)
            self.users[user.username] = user
            return self.users[user.username]

    def remove_user(self, staff, user):
        if staff._role != UserRole.CUSTOMER:
            if user.username in self.users:
                del self.users[user.username]
                return f"User {user.username} removed."
            else:
                return f"User {user.username} does not exist."
        else:
            raise PermissionError("Only staff can remove users.")

    def create_account(self, user, account_number, account_type, account_balance, owner_id, branch_code):
        if user._role != UserRole.CUSTOMER:
            if branch_code in self.branch_codes:
                branch = self.branch_codes[branch_code]
                account = Accounts(account_number, account_type, account_balance, owner_id)
                branch.add_account(account)
                return f"Account {account_number} created for owner {owner_id} in branch {branch_code}."
            else:
                raise ValueError(f"Branch code {branch_code} does not exist.")
        else:
            raise PermissionError("Only staff can create accounts.")
            
    def remove_account(self, user, account_number, branch_code):
        if user._role != UserRole.CUSTOMER:
            if branch_code in self.branch_codes:
                branch = self.branch_codes[branch_code]
                account = branch.get_account(account_number)
                if account:
                    branch.remove_account(account)
                    return f"Account {account_number} removed from branch {branch_code}."
                else:
                    return f"Account {account_number} does not exist in branch {branch_code}."
            else:
                raise ValueError(f"Branch code {branch_code} does not exist.")
        else:
            raise PermissionError("Only staff can remove accounts.")



    def __str__(self):
        return f"Bank Name: {self.bank_name}, Branches: {list(self.branch_codes.keys())}, Users: {list(self.users.keys())}"
    
        