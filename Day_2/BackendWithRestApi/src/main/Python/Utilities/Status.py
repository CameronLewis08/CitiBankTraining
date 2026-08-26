from enum import Enum


class OutcomeStatus(Enum):
    SUCCESS = "Success"
    FAILURE = "Failure"


class AccountType(Enum):
    CHECKING = "Checking"
    SAVINGS = "Savings"


class AccountStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class UserRole(Enum):
    ADMIN = "Admin"
    MANAGER = "Manager"
    STAFF = "Staff"
    CUSTOMER = "Customer"
