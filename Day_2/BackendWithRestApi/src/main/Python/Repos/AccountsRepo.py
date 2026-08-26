
from Utilities.Database import get_database
from Models.Accounts import Accounts
from pymongo.errors import DuplicateKeyError

class AccountsRepository:

    @staticmethod
    def get_all_accounts() -> list:
        collection = get_database().accounts
        return [Accounts(doc["account_id"], doc["customer_id"], doc["balance"]) for doc in collection.find()]

    @staticmethod
    def get_account_by_id(account_id: str) -> Accounts:
        if not account_id:
            raise ValueError("Account ID must be provided.")
        
        collection = get_database().accounts
        doc = collection.find_one({"account_id": account_id})
        return Accounts(doc["account_id"], doc["customer_id"], doc["balance"]) if doc else None

    @staticmethod
    def create_account(account_data: dict) -> Accounts:
        if not account_data.get("account_id") or not account_data.get("customer_id") or "balance" not in account_data:
            raise ValueError("Account data must include 'account_id', 'customer_id', and 'balance' fields.")

        account = Accounts(account_data["account_id"], account_data["customer_id"], account_data["balance"])

        collection = get_database().accounts
        try:
            collection.insert_one(account.to_dict())
        except DuplicateKeyError:
            raise ValueError(f"Account with ID {account_data['account_id']} already exists.")

        return account

    @staticmethod
    def update_account(account_id: str, account_data: dict) -> Accounts:
        if not account_id:
            raise ValueError("Account ID must be provided for update.")
        
        if not account_data or not account_data.get("customer_id") or "balance" not in account_data:
            raise ValueError("Account data must include both 'customer_id' and 'balance' fields for update.")
        
        if "account_id" in account_data and account_data["account_id"] != account_id:
            raise ValueError("Account ID in the data does not match the provided account ID.")

        account = AccountsRepository.get_account_by_id(account_id)
        if account is None:
            raise ValueError(f"Account with ID {account_id} does not exist.")

        if "customer_id" in account_data:
            account.set_customer_id(account_data["customer_id"])
        if "balance" in account_data:
            account.set_balance(account_data["balance"])

        collection = get_database().accounts
        collection.update_one({"account_id": account_id}, {"$set": {"customer_id": account.get_customer_id(), "balance": account.get_balance()}})
        
        return account

    @staticmethod
    def delete_account(account_id: str) -> bool:
        if not account_id:
            raise ValueError("Account ID must be provided for deletion.")
        
        collection = get_database().accounts
        result = collection.delete_one({"account_id": account_id})
        return result.deleted_count > 0

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

        # Update both accounts in the database
        AccountsRepository.update_account(
            source_account.get_account_id(),
            {"customer_id": source_account.get_customer_id(), "balance": source_account.get_balance()},
        )
        AccountsRepository.update_account(
            target_account.get_account_id(),
            {"customer_id": target_account.get_customer_id(), "balance": target_account.get_balance()},
        )