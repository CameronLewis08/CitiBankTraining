
"""
Account Repository for the Banking Domain REST API:
    This module defines the AccountsRepository class, which provides methods for interacting with account data,
    including fund transfers between accounts.
    Storage is an in-memory dictionary (no external database).
"""

from Models.Accounts import Accounts

_accounts: dict[str, Accounts] = {
    "ACC-1001": Accounts("ACC-1001", 1, 500.00),
    "ACC-1002": Accounts("ACC-1002", 2, 1250.75),
    "ACC-1003": Accounts("ACC-1003", 2, 300.00),
    "ACC-1004": Accounts("ACC-1004", 3, 0.00),
}


class AccountsRepository:

    @staticmethod
    def get_all_accounts() -> list:
        return list(_accounts.values())

    @staticmethod
    def get_account_by_id(account_id: str) -> Accounts:
        if not account_id:
            raise ValueError("Account ID must be provided.")

        return _accounts.get(account_id)

    @staticmethod
    def create_account(account_data: dict) -> Accounts:
        if not account_data.get("account_id") or not account_data.get("customer_id") or "balance" not in account_data:
            raise ValueError("Account data must include 'account_id', 'customer_id', and 'balance' fields.")

        account_id = account_data["account_id"]
        if account_id in _accounts:
            raise ValueError(f"Account with ID {account_id} already exists.")

        account = Accounts(account_id, account_data["customer_id"], account_data["balance"])
        _accounts[account_id] = account
        return account

    @staticmethod
    def update_account(account_id: str, account_data: dict) -> Accounts:
        if not account_id:
            raise ValueError("Account ID must be provided for update.")

        if not account_data or not account_data.get("customer_id") or "balance" not in account_data:
            raise ValueError("Account data must include both 'customer_id' and 'balance' fields for update.")

        if "account_id" in account_data and account_data["account_id"] != account_id:
            raise ValueError("Account ID in the data does not match the provided account ID.")

        account = _accounts.get(account_id)
        if account is None:
            raise ValueError(f"Account with ID {account_id} does not exist.")

        if "customer_id" in account_data:
            account.set_customer_id(account_data["customer_id"])
        if "balance" in account_data:
            account.set_balance(account_data["balance"])

        return account

    @staticmethod
    def delete_account(account_id: str) -> bool:
        if not account_id:
            raise ValueError("Account ID must be provided for deletion.")

        if account_id not in _accounts:
            return False

        del _accounts[account_id]
        return True

    @staticmethod
    def transfer_funds(source_account_id: str, target_account_id: str, amount: float) -> None:
        if not source_account_id or not target_account_id:
            raise ValueError("Both source and target account IDs must be provided.")
        if amount <= 0:
            raise ValueError("Transfer amount must be positive.")

        source_account = AccountsRepository.get_account_by_id(source_account_id)
        target_account = AccountsRepository.get_account_by_id(target_account_id)

        if source_account is None:
            raise ValueError(f"Source account with ID {source_account_id} does not exist.")
        if target_account is None:
            raise ValueError(f"Target account with ID {target_account_id} does not exist.")

        source_account.transfer(target_account, amount)
