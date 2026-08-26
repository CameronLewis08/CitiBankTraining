"""
Account Model for the Banking Domain REST API:
    Defines the Accounts abstract base class and its CheckingAccount /
    SavingsAccount subclasses. Ported from Day_1's console-app account
    hierarchy: Checking allows a $500 overdraft, Savings never goes
    negative, and every deposit/withdraw/transfer is recorded in an
    in-memory transaction history that gets persisted alongside the
    account document.
"""

import time
from abc import ABC, abstractmethod
from typing import override

from Utilities.Status import AccountType, AccountStatus, OutcomeStatus

OVERDRAFT_LIMIT = 500


class Accounts(ABC):
    """Abstract base class for all bank accounts. Use CheckingAccount or SavingsAccount."""

    def __init__(self, account_id, owner_id, balance, branch_code, account_type=None,
                 status=AccountStatus.ACTIVE, transaction_history=None):
        self.set_account_id(account_id)
        self.set_owner_id(owner_id)
        self._balance = balance
        self.branch_code = branch_code
        self.account_type = account_type
        self.status = status if isinstance(status, AccountStatus) else AccountStatus(status)
        self.transaction_history = transaction_history if transaction_history is not None else []

    def get_account_id(self):
        return self._account_id

    def get_owner_id(self):
        return self._owner_id

    def get_balance(self):
        return self._balance

    def get_branch_code(self):
        return self.branch_code

    def get_account_type(self):
        return self.account_type

    def get_status(self):
        return self.status

    def get_transaction_history(self):
        return self.transaction_history

    def is_active(self):
        return self.status == AccountStatus.ACTIVE

    def set_account_id(self, account_id):
        if not account_id:
            raise ValueError("Account ID cannot be empty.")
        self._account_id = account_id

    def set_owner_id(self, owner_id):
        if not owner_id:
            raise ValueError("Owner ID cannot be empty.")
        self._owner_id = owner_id

    def set_balance(self, balance):
        if balance < 0:
            raise ValueError("Initial balance cannot be negative.")
        self._balance = balance

    def deactivate_account(self):
        self.status = AccountStatus.INACTIVE

    def reactivate_account(self):
        self.status = AccountStatus.ACTIVE

    def add_transaction(self, transaction):
        self.transaction_history.append(transaction)

    def deposit(self, amount):
        if amount > 0 and self.is_active():
            self._balance += amount
            self.add_transaction({"type": "deposit", "amount": amount,
                                   "status": OutcomeStatus.SUCCESS.value, "timestamp": time.time()})
            return {"status": OutcomeStatus.SUCCESS.value, "type": "deposit", "amount": amount}

        self.add_transaction({"type": "deposit", "amount": amount,
                               "status": OutcomeStatus.FAILURE.value, "timestamp": time.time()})
        return {"status": OutcomeStatus.FAILURE.value, "type": "deposit", "amount": amount}

    @abstractmethod
    def withdraw(self, amount):
        ...

    def transfer(self, amount, target_account):
        if target_account.is_active() and self.withdraw(amount)["status"] == OutcomeStatus.SUCCESS.value:
            target_account.deposit(amount)
            self.add_transaction({"type": "transfer", "amount": amount,
                                   "status": OutcomeStatus.SUCCESS.value, "timestamp": time.time()})
            return {"status": OutcomeStatus.SUCCESS.value, "type": "transfer", "amount": amount}

        self.add_transaction({"type": "transfer", "amount": amount,
                               "status": OutcomeStatus.FAILURE.value, "timestamp": time.time()})
        return {"status": OutcomeStatus.FAILURE.value, "type": "transfer", "amount": amount}

    def to_dict(self):
        return {
            "account_id": self._account_id,
            "owner_id": self._owner_id,
            "balance": self._balance,
            "branch_code": self.branch_code,
            "account_type": self.account_type.value if isinstance(self.account_type, AccountType) else self.account_type,
            "status": self.status.value,
            "transaction_history": self.transaction_history,
        }

    def __repr__(self):
        type_label = self.account_type.value if isinstance(self.account_type, AccountType) else self.account_type
        return (f"Account ID: {self._account_id}, Type: {type_label}, Balance: {self._balance}, "
                f"Owner ID: {self._owner_id}, Status: {self.status.value}")


class CheckingAccount(Accounts):
    def __init__(self, account_id, owner_id, balance, branch_code,
                 status=AccountStatus.ACTIVE, transaction_history=None):
        super().__init__(account_id, owner_id, balance, branch_code, AccountType.CHECKING,
                          status, transaction_history)

    @override
    def withdraw(self, amount):
        if self.is_active() and amount > 0 and amount <= OVERDRAFT_LIMIT + self._balance:
            self._balance -= amount
            self.add_transaction({"type": "withdrawal", "amount": amount,
                                   "status": OutcomeStatus.SUCCESS.value, "timestamp": time.time()})
            return {"status": OutcomeStatus.SUCCESS.value, "type": "withdrawal", "amount": amount}

        self.add_transaction({"type": "withdrawal", "amount": amount,
                               "status": OutcomeStatus.FAILURE.value, "timestamp": time.time()})
        return {"status": OutcomeStatus.FAILURE.value, "type": "withdrawal", "amount": amount}


class SavingsAccount(Accounts):
    def __init__(self, account_id, owner_id, balance, branch_code,
                 status=AccountStatus.ACTIVE, transaction_history=None):
        super().__init__(account_id, owner_id, balance, branch_code, AccountType.SAVINGS,
                          status, transaction_history)

    @override
    def withdraw(self, amount):
        if self.is_active() and 0 < amount <= self._balance:
            self._balance -= amount
            self.add_transaction({"type": "withdrawal", "amount": amount,
                                   "status": OutcomeStatus.SUCCESS.value, "timestamp": time.time()})
            return {"status": OutcomeStatus.SUCCESS.value, "type": "withdrawal", "amount": amount}

        self.add_transaction({"type": "withdrawal", "amount": amount,
                               "status": OutcomeStatus.FAILURE.value, "timestamp": time.time()})
        return {"status": OutcomeStatus.FAILURE.value, "type": "withdrawal", "amount": amount}


def build_account(account_type, account_id, owner_id, balance, branch_code,
                   status=AccountStatus.ACTIVE, transaction_history=None):
    resolved_type = account_type if isinstance(account_type, AccountType) else None
    if resolved_type is None:
        try:
            resolved_type = AccountType(account_type)
        except ValueError:
            resolved_type = None

    if resolved_type == AccountType.CHECKING:
        return CheckingAccount(account_id, owner_id, balance, branch_code, status, transaction_history)
    if resolved_type == AccountType.SAVINGS:
        return SavingsAccount(account_id, owner_id, balance, branch_code, status, transaction_history)
    raise ValueError(f"Unknown account type: {account_type}")
