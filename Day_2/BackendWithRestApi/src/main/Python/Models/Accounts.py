
from abc import ABC



class Accounts(ABC):
    def __init__(self, account_id, customer_id, balance):
        self.set_account_id(account_id)
        self.set_customer_id(customer_id)
        self.set_balance(balance)

    def get_account_id(self):
        return self._account_id

    def get_customer_id(self):
        return self._customer_id

    def get_balance(self):
        return self._balance

    def set_balance(self, balance):
        if balance < 0:
            raise ValueError("Balance cannot be negative.")
        self._balance = balance

    def set_account_id(self, account_id):
        if not account_id:
            raise ValueError("Account ID cannot be empty.")
        else:
            self._account_id = account_id
            return f"Account ID updated to {account_id}."
        
    def set_customer_id(self, customer_id):
        if not customer_id:
            raise ValueError("Customer ID cannot be empty.")
        else:
            self._customer_id = customer_id
            return f"Customer ID updated to {customer_id}."
        

    def transfer(self, target_account, amount):
        if amount <= 0:
            raise ValueError("Transfer amount must be positive.")
        if self.get_balance() < amount:
            raise ValueError("Insufficient funds in the source account.")

        self.set_balance(self.get_balance() - amount)
        target_account.set_balance(target_account.get_balance() + amount)

    

    def to_dict(self):
        return {
            "account_id": self._account_id,
            "customer_id": self._customer_id,
            "balance": self._balance
        }
