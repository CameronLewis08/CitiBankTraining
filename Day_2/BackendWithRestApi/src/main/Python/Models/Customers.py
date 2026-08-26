"""
Customer Model for the Banking Domain REST API:
    This module defines the Customer class, which represents a customer in the banking domain. The Customer class contains attributes such as customer ID, name, email, and account information. It also includes methods for customer management.
    This module should be used in conjunction with other modules in the banking domain to provide a complete banking application experience.
"""

from Models.Accounts import Accounts


class Customers:
    def __init__(self, customer_id, name, email, accounts=None):
        self.set_customer_id(customer_id)
        self.set_name(name)
        self.set_email(email)
        self.accounts = accounts if accounts is not None else []

    def get_customer_id(self):
        return self.customer_id

    def get_name(self):
        return self.name

    def get_email(self):
        return self.email

    def get_account(self, account_id):
        if not account_id:
            raise ValueError("Account ID must be provided.")
        for account in self.accounts:
            if account.get_account_id() == account_id:
                return account
        raise ValueError(f"Account with ID {account_id} does not exist for this customer.")

    def get_all_accounts(self):
        return self.accounts

    def set_customer_id(self, new_customer_id):
        if not new_customer_id:
            raise ValueError("Customer ID cannot be empty.")
        else:
            self.customer_id = new_customer_id
            return f"Customer ID updated to {new_customer_id}."

    def set_name(self, new_name):
        if not new_name:
            raise ValueError("Name cannot be empty.")
        else:
            self.name = new_name
            return f"Name updated to {new_name}."
        
    def set_email(self, new_email):
        if not new_email:
            raise ValueError("Email cannot be empty")
        elif "@" not in new_email or "." not in new_email:
            raise ValueError("Invalid email format missing '@' or '.'")
        else:
            self.email = new_email
            return f"Email updated to {new_email}."

    def add_account(self, account):
        if not isinstance(account, Accounts):
            raise ValueError("Invalid account type.")
        self.accounts.append(account)

    def delete_account(self, account_id):
        if not account_id:
            raise ValueError("Account ID must be provided.")
        for i, account in enumerate(self.accounts):
            if account.get_account_id() == account_id:
                del self.accounts[i]
                return True
        raise ValueError(f"Account with ID {account_id} does not exist for this customer.")

    def to_dict(self) -> dict:
        return {
            "customer_id": self.customer_id,
            "name": self.name,
            "email": self.email,
            "accounts": [account.to_dict() for account in self.accounts],
        }

    def __repr__(self):
        return f"Customer ID: {self.customer_id}, Name: {self.name}, Email: {self.email}"
