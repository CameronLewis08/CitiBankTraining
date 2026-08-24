"""
Bank Model for the Banking Domain Console Application:
    This module defines the Bank class, which represents a bank in the banking domain. The Bank class contains attributes such as bank name, branch name, and a list of users associated with the bank. It also includes methods for managing users and performing banking operations.
    This module should be used in conjunction with other modules in the banking domain to provide a complete banking application experience.

"""

from Models.users import Users, UserRole
from Models.branches import Branches
from status import AccountType, OutcomeStatus
from Models.accounts import CheckingAccount, SavingsAccount

class Banks:
    def __init__(self, bank_name, branch_codes=None, users=None):
        self.bank_name = bank_name
        self.branch_codes = branch_codes if branch_codes is not None else {}
        self.users = users if users is not None else {}

    def get_bank_name(self):
        return f"Bank Name: {self.bank_name}"
    
    def get_branch_codes(self, staff):
        if staff.get_role() == UserRole.CUSTOMER:
            raise PermissionError("Only Staff can view all branch codes.")
        else: 
            return f"Branch Codes: {self.branch_codes}"

    def get_users(self, staff):
        if staff.get_role() == UserRole.CUSTOMER:
            raise PermissionError("Only Staff can view all users.")
        else: 
            return f"Users: {self.users}"

    
    def create_branch(self, staff, branch_code, location, manager_id, staff_list):
        if staff.get_role() != UserRole.ADMIN:
            raise PermissionError("Only Admins can create branches.")
        else:
            if branch_code in self.branch_codes:
                raise ValueError(f"Branch code {branch_code} already exists.")
                
            branch = Branches(branch_code, location, manager_id, staff_list)
            self.branch_codes[branch_code] = branch

            return f"{OutcomeStatus.SUCCESS.value}, Branch {branch_code} created at {location} with manager {manager_id}."
    
    def remove_branch(self, staff, branch_code):
        if staff.get_role() != UserRole.ADMIN:
            raise PermissionError("Only Admins can remove branches.")
        else:
            if branch_code in self.branch_codes:
                del self.branch_codes[branch_code]
            else:
                raise ValueError(f"Branch code {branch_code} does not exist.")
            
        return f"{OutcomeStatus.SUCCESS.value}, Branch {branch_code} removed."

    def create_user(self, staff, username, password, role, email, branch_code):
        if staff.get_role() not in [UserRole.ADMIN, UserRole.MANAGER]:
            raise PermissionError("Only Admins and Managers can create users.")
        else:
            if username in self.users:
                raise ValueError(f"User {username} already exists.")
            
            new_user = Users(username, password, role, email, branch_code)
            self.users[username] = new_user
            
            return f"{OutcomeStatus.SUCCESS.value}, User {username} created with role {role.value} in branch {branch_code}."


    def remove_user(self, staff, user):
        if staff.get_role() not in [UserRole.ADMIN, UserRole.MANAGER]:
            raise PermissionError("Only Admins and Managers can remove users.")
        else:
            if user.get_username() in self.users:
                del self.users[user.get_username()]
                return f"{OutcomeStatus.SUCCESS.value}, User {user.get_username()} removed."
            else:
                raise ValueError(f"User {user.get_username()} does not exist.")

    def create_account(self, staff, account_number, account_type, account_balance, owner_id, branch_code):
        if staff.get_role() in [UserRole.ADMIN, UserRole.MANAGER, UserRole.STAFF]:
            if branch_code in self.branch_codes:
                if account_number in [acc.account_number for acc in self.branch_codes[branch_code].get_accounts()]:
                    raise ValueError(f"Account number {account_number} already exists in branch {branch_code}.")
                
                branch = self.branch_codes[branch_code]
                if account_type == AccountType.CHECKING:
                    account = CheckingAccount(account_number, account_balance, owner_id)
                elif account_type == AccountType.SAVINGS:
                    account = SavingsAccount(account_number, account_balance, owner_id)
                else:
                    raise ValueError(f"Unknown account type: {account_type}")
                branch.add_account(account)
                return f"{OutcomeStatus.SUCCESS.value}, Account {account_number} created for owner {owner_id} in branch {branch_code}."
            else:
                raise ValueError(f"Branch code {branch_code} does not exist.")
        else:
            raise PermissionError("Only Admins, Managers, and Staff can create accounts.")
            
    def remove_account(self, staff, account_number, branch_code):
        if staff.get_role() in [UserRole.ADMIN, UserRole.MANAGER, UserRole.STAFF]:
            if branch_code in self.branch_codes:
                branch = self.branch_codes[branch_code]
                account = branch.get_account(account_number)
                if account:
                    branch.remove_account(account_number)
                    return f"{OutcomeStatus.SUCCESS.value}, Account {account_number} removed from branch {branch_code}."
                else:
                    return f"{OutcomeStatus.FAILURE.value}, Account {account_number} does not exist in branch {branch_code}."
            else:
                raise ValueError(f"Branch code {branch_code} does not exist.")
        else:
            raise PermissionError("Only Admins, Managers, and Staff can remove accounts.")




    def __repr__(self):
        return f"Bank Name: {self.bank_name}, Branches: {list(self.branch_codes.keys())}, Users: {list(self.users.keys())}"
    
        