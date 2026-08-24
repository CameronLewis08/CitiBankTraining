"""
Account Model for the Banking Domain Console Application:
    This module defines the Account class, which represents an account in the banking domain. The Account class contains attributes such as account number, account type, and account balance. It also includes methods for managing account information and performing account operations.
    This module should be used in conjunction with other modules in the banking domain to provide a complete banking application experience.
    
"""


import time
from typing import override
from Models.users import UserRole
from status import AccountType, OutcomeStatus
from abc import ABC, abstractmethod

Overdraft_limit = 500  # Example overdraft limit for checking accounts


class Accounts(ABC):
    """Abstract base class for all bank accounts. Cannot be instantiated directly - use CheckingAccount or SavingsAccount."""

    def __init__(self, account_number, account_type, account_balance, owner_id, is_active=True):
        self.account_number = account_number
        self.account_type = account_type
        self.account_balance = account_balance
        self.owner_id = owner_id
        self.transaction_history = []
        self.is_active = is_active

    def get_account_number(self):
        return self.account_number

    def get_account_type(self):
        return self.account_type

    def get_account_balance(self):
        return self.account_balance

    def get_transaction_history(self):
        return self.transaction_history

    def get_balance(self):
        return self.account_balance
    
    def get_last_transaction(self):
        if self.transaction_history:
            return self.transaction_history[-1]
        
        return None
    
    def get_status(self):
        return self.is_active

    def set_owner_id(self, user, new_owner_id):
        if user.get_role() == UserRole.MANAGER:
            self.owner_id = new_owner_id
        else:
            raise PermissionError("Only Managers can change account ownership.")

    def deposit(self, amount):
        if amount > 0 and self.is_active:
            self.account_balance += amount
            self.add_transaction({"type": "deposit", "amount": amount, "status": OutcomeStatus.SUCCESS, "timestamp": time.time()})
            return {"status": OutcomeStatus.SUCCESS, "type": "deposit", "amount": amount}
        
        self.add_transaction({"type": "deposit", "amount": amount, "status": OutcomeStatus.FAILURE, "timestamp": time.time()})
        return {"status": OutcomeStatus.FAILURE, "type": "deposit", "amount": amount}

    @abstractmethod
    def withdraw(self, amount):
        ...

    def transfer(self, amount, target_account):
        if target_account.is_active and self.withdraw(amount)["status"] == OutcomeStatus.SUCCESS:
            target_account.deposit(amount)
            self.add_transaction({"type": "transfer", "amount": amount, "status": OutcomeStatus.SUCCESS, "timestamp": time.time()})
            return {"status": OutcomeStatus.SUCCESS, "type": "transfer", "amount": amount}

        self.add_transaction({"type": "transfer", "amount": amount, "status": OutcomeStatus.FAILURE, "timestamp": time.time()})
        return {"status": OutcomeStatus.FAILURE, "type": "transfer", "amount": amount}

    def add_transaction(self, transaction):
        self.transaction_history.append(transaction)

    def reactivate_account(self):
            self.is_active = True

    def deactivate_account(self):
        self.is_active = False

    def __repr__(self):
        return f"Account Number: {self.account_number}, Type: {self.account_type.value}, Balance: {self.account_balance}, Owner ID: {self.owner_id}, Active: {self.is_active}"



class CheckingAccount(Accounts):
    def __init__(self, account_number, account_balance, owner_id):
        super().__init__(account_number, AccountType.CHECKING, account_balance, owner_id)

    @override
    def withdraw(self, amount):
        if self.is_active and amount > 0 and amount <= Overdraft_limit + self.account_balance:
            self.account_balance -= amount
            self.add_transaction({"type": "withdrawal", "amount": amount, "status": OutcomeStatus.SUCCESS, "timestamp": time.time()})
            return {"status": OutcomeStatus.SUCCESS, "type": "withdrawal", "amount": amount}

        self.add_transaction({"type": "withdrawal", "amount": amount, "status": OutcomeStatus.FAILURE, "timestamp": time.time()})
        return {"status": OutcomeStatus.FAILURE, "type": "withdrawal", "amount": amount}


class SavingsAccount(Accounts):
    def __init__(self, account_number, account_balance, owner_id):
        super().__init__(account_number, AccountType.SAVINGS, account_balance, owner_id)

    @override
    def withdraw(self, amount):
        if self.is_active and 0 < amount <= self.account_balance:
            self.account_balance -= amount
            self.add_transaction({"type": "withdrawal", "amount": amount, "status": OutcomeStatus.SUCCESS, "timestamp": time.time()})
            return {"status": OutcomeStatus.SUCCESS, "type": "withdrawal", "amount": amount}

        self.add_transaction({"type": "withdrawal", "amount": amount, "status": OutcomeStatus.FAILURE, "timestamp": time.time()})
        return {"status": OutcomeStatus.FAILURE, "type": "withdrawal", "amount": amount}



