"""
Account Model for the Banking Domain Console Application:
    This module defines the Account class, which represents an account in the banking domain. The Account class contains attributes such as account number, account type, and account balance. It also includes methods for managing account information and performing account operations.
    This module should be used in conjunction with other modules in the banking domain to provide a complete banking application experience.
    
"""

from enum import Enum, auto
from typing import override

Overdraft_limit = 500  # Example overdraft limit for checking accounts

class AccountType(Enum):
    CHECKING = "Checking"
    SAVINGS = "Savings"

class TransactionStatus(Enum):
    SUCCESS = "Success"
    FAILURE = "Failure"




class Accounts:
    def __init__(self, account_number, account_type, account_balance, owner_id, is_active=True):
        self.account_number = account_number
        self.account_type = account_type
        self.account_balance = account_balance
        self.owner_id = owner_id
        self.transaction_history = []
        self.is_active = is_active


    def get_account_info(self):
        return {
            "account_number": self.account_number,
            "account_type": self.account_type.value,
            "account_balance": self.account_balance,
            "owner_id": self.owner_id,
            "is_active": self.is_active
        }

    def get_transaction_history(self):
        return self.transaction_history

    def get_balance(self):
        return self.account_balance
    
    def get_last_transaction(self):
        if self.transaction_history:
            return self.transaction_history[-1]
        
        return None
    

    def deposit(self, amount):
        if amount > 0:
            self.account_balance += amount
            self.add_transaction({"type": "deposit", "amount": amount, "status": TransactionStatus.SUCCESS})
            return {"status": TransactionStatus.SUCCESS, "type": "deposit", "amount": amount}
        
        self.add_transaction({"type": "deposit", "amount": amount, "status": TransactionStatus.FAILURE})
        return {"status": TransactionStatus.FAILURE, "type": "deposit", "amount": amount}

    def withdraw(self, amount):
        if 0 < amount <= self.account_balance:
            self.account_balance -= amount
            self.add_transaction({"type": "withdrawal", "amount": amount, "status": TransactionStatus.SUCCESS})

            return {"status": TransactionStatus.SUCCESS, "type": "withdrawal", "amount": amount}

        self.add_transaction({"type": "withdrawal", "amount": amount, "status": TransactionStatus.FAILURE})
        return {"status": TransactionStatus.FAILURE, "type": "withdrawal", "amount": amount}
    
    def transfer(self, amount, target_account):
        if self.withdraw(amount)["status"] == TransactionStatus.SUCCESS:
            target_account.deposit(amount)
            self.add_transaction({"type": "transfer", "amount": amount, "status": TransactionStatus.SUCCESS})
            return {"status": TransactionStatus.SUCCESS, "type": "transfer", "amount": amount}

        self.add_transaction({"type": "transfer", "amount": amount, "status": TransactionStatus.FAILURE})
        return {"status": TransactionStatus.FAILURE, "type": "transfer", "amount": amount}

    def add_transaction(self, transaction):
        self.transaction_history.append(transaction)

    def is_account_active(self):
        return self.is_active

    def __str__(self):
        return f"Account Number: {self.account_number}, Type: {self.account_type.value}, Balance: {self.account_balance}, Owner ID: {self.owner_id}, Active: {self.is_active}"


class CheckingAccount(Accounts):
    def __init__(self, account_number, account_balance, owner_id):
        super().__init__(account_number, AccountType.CHECKING, account_balance, owner_id)

    @override
    def withdraw(self, amount):
        if amount > 0 and amount <= Overdraft_limit + self.account_balance:
            self.account_balance -= amount
            self.add_transaction({"type": "withdrawal", "amount": amount, "status": TransactionStatus.SUCCESS})
            return {"status": TransactionStatus.SUCCESS, "type": "withdrawal", "amount": amount}

        self.add_transaction({"type": "withdrawal", "amount": amount, "status": TransactionStatus.FAILURE})
        return {"status": TransactionStatus.FAILURE, "type": "withdrawal", "amount": amount}


class SavingsAccount(Accounts):
    def __init__(self, account_number, account_balance, owner_id):
        super().__init__(account_number, AccountType.SAVINGS, account_balance, owner_id)



