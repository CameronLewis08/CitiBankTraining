

from enum import Enum


class OutcomeStatus(Enum):
    SUCCESS = "Success"
    FAILURE = "Failure"

class AccountType(Enum):
    CHECKING = "Checking"
    SAVINGS = "Savings"

class UserRole(Enum):
    ADMIN = "Admin"
    MANAGER = "Manager"
    STAFF = "Staff"
    CUSTOMER = "Customer"