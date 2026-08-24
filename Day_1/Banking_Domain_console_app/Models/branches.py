"""
Branch Model for the Banking Domain Console Application:
    This module defines the Branch class, which represents a branch of a bank. The Branch class contains attributes such as branch name, address, and a list of accounts associated with the branch. It also includes methods for managing accounts and performing banking operations.
    This module should be used in conjunction with other modules in the banking domain to provide a complete banking application experience.
"""


from Models.users import UserRole
from status import OutcomeStatus

class Branches:
    def __init__(self, branch_code, location, manager_id, staff_list, accounts=None):
        self.branch_code = branch_code
        self.location = location
        self.__manager_id = manager_id
        self.__staff_list = staff_list
        self.accounts = accounts if accounts is not None else {}
        
    def get_branch_code(self):
        return f"Branch Code: {self.branch_code}"
    
    def get_location(self):
        return f"Location: {self.location}"
    
    def get_manager_id(self, staff):
        if staff.get_role() == UserRole.CUSTOMER:
            raise PermissionError("Only staff can view the branch manager.")
        else:
            if self.__manager_id is not None:
                return f"Manager: {self.__manager_id}"
            else:
                return f"{OutcomeStatus.FAILURE.value}, No manager assigned to branch {self.branch_code}."

    def get_staff_list(self, staff):
        if staff.get_role() == UserRole.CUSTOMER:
            raise PermissionError("Only staff can view the branch staff list.")
        else:
            return f"Staff List: {self.__staff_list}"

    def get_accounts(self):
        return list(self.accounts.values())
        
    def get_account(self, account_number):
        return self.accounts.get(account_number)
            
    def add_account(self, account):
        self.accounts[account.account_number] = account
        return f"{OutcomeStatus.SUCCESS.value}, Account {account.account_number} added to branch {self.branch_code}."

    def remove_account(self, account_number): 
        if account_number in self.accounts:
            del self.accounts[account_number]
            return f"{OutcomeStatus.SUCCESS.value}, Account {account_number} removed from branch {self.branch_code}."
        else:
            return f"{OutcomeStatus.FAILURE.value}, Account {account_number} does not exist in branch {self.branch_code}."
    
    def set_manager(self, staff, manager_id):
        if staff.get_role() in [UserRole.CUSTOMER, UserRole.STAFF]:
            return f"{OutcomeStatus.FAILURE.value}, User {staff.username} is not a manager or admin and cannot alter the branch manager."
        else:
            self.__manager_id = manager_id
            return f"{OutcomeStatus.SUCCESS.value}, Manager {manager_id} assigned to branch {self.branch_code}."

    def set_location(self, staff, new_location):
            if staff.get_role() != UserRole.ADMIN:
                raise PermissionError("Only Admins can change the branch location.")
            else:
                self.location = new_location
                return f"{OutcomeStatus.SUCCESS.value}, Location updated to {new_location} for branch {self.branch_code}."
            

    def __repr__(self):
        return f"Branch Code: {self.branch_code}, Location: {self.location}, Manager ID: {self.__manager_id}, Staff List: {self.__staff_list}"
    
    
    

    
