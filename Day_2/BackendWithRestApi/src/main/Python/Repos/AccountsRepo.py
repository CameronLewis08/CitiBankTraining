"""
Account Repository for the Banking Domain REST API:
    CRUD + deposit/withdraw/transfer against the 'accounts' MongoDB
    collection. Balance only ever changes through deposit/withdraw/
    transfer (never a direct PUT), so overdraft rules and transaction
    history stay consistent.
"""

import re

from Utilities.Database import get_database
from Models.Accounts import build_account
from Utilities.Status import AccountType, AccountStatus
from pymongo.errors import DuplicateKeyError


def _to_account(doc):
    return build_account(
        AccountType(doc["account_type"]),
        doc["account_id"],
        doc["owner_id"],
        doc["balance"],
        doc["branch_code"],
        status=AccountStatus(doc.get("status", AccountStatus.ACTIVE.value)),
        transaction_history=doc.get("transaction_history", []),
    )


class AccountsRepository:

    @staticmethod
    def _find_accounts(base_query, skip=0, limit=None, search=None):
        # search needs the owner's name, which only lives on the users
        # collection - a plain find() can't reach across collections, so
        # the search path switches to an aggregation with a $lookup join.
        # Non-search calls stay on plain find() (cheaper, no join) since
        # that's the common case (every unpaginated caller in this repo).
        collection = get_database().accounts
        if search:
            pattern = re.escape(search)
            pipeline = [
                {"$match": base_query},
                {"$lookup": {
                    "from": "users", "localField": "owner_id",
                    "foreignField": "user_id", "as": "owner",
                }},
                {"$unwind": {"path": "$owner", "preserveNullAndEmptyArrays": True}},
                {"$match": {"$or": [
                    {"account_id": {"$regex": pattern, "$options": "i"}},
                    {"branch_code": {"$regex": pattern, "$options": "i"}},
                    {"account_type": {"$regex": pattern, "$options": "i"}},
                    {"owner.name": {"$regex": pattern, "$options": "i"}},
                ]}},
            ]
            if skip:
                pipeline.append({"$skip": skip})
            if limit is not None:
                pipeline.append({"$limit": limit})
            return [_to_account(doc) for doc in collection.aggregate(pipeline)]

        cursor = collection.find(base_query).skip(skip)
        if limit is not None:
            cursor = cursor.limit(limit)
        return [_to_account(doc) for doc in cursor]

    @staticmethod
    def get_all_accounts(owner_id=None, skip=0, limit=None, search=None):
        base_query = {"owner_id": owner_id} if owner_id is not None else {}
        return AccountsRepository._find_accounts(base_query, skip, limit, search)

    @staticmethod
    def get_account_by_id(account_id, owner_id=None):
        if not account_id:
            raise ValueError("Account ID must be provided.")

        collection = get_database().accounts
        query = {"account_id": account_id}
        if owner_id is not None:
            # Scope the lookup so someone else's account looks identical to
            # one that doesn't exist at all.
            query["owner_id"] = owner_id
        doc = collection.find_one(query)
        return _to_account(doc) if doc else None

    @staticmethod
    def get_accounts_by_branch(branch_code, skip=0, limit=None, search=None):
        return AccountsRepository._find_accounts({"branch_code": branch_code}, skip, limit, search)

    @staticmethod
    def search_accounts_by_branch(branch_code, account_type=None, status=None):
        query = {"branch_code": branch_code}
        if account_type is not None:
            query["account_type"] = account_type
        if status is not None:
            query["status"] = status
        collection = get_database().accounts
        return [_to_account(doc) for doc in collection.find(query)]

    @staticmethod
    def create_account(account_data: dict):
        required = ("account_id", "owner_id", "balance", "branch_code", "account_type")
        if not all(field in account_data and account_data[field] not in (None, "") for field in required):
            raise ValueError(
                "Account data must include 'account_id', 'owner_id', 'balance', 'branch_code', and 'account_type' fields."
            )

        if account_data["balance"] < 0:
            raise ValueError("Initial balance cannot be negative.")

        account = build_account(
            account_data["account_type"],
            account_data["account_id"],
            account_data["owner_id"],
            account_data["balance"],
            account_data["branch_code"],
        )

        collection = get_database().accounts
        try:
            collection.insert_one(account.to_dict())
        except DuplicateKeyError:
            raise ValueError(f"Account with ID {account_data['account_id']} already exists.")

        return account

    @staticmethod
    def _save(account):
        collection = get_database().accounts
        collection.update_one({"account_id": account.get_account_id()}, {"$set": account.to_dict()})
        return account

    @staticmethod
    def deposit(account_id, amount, requesting_user_id=None):
        account = AccountsRepository.get_account_by_id(account_id, requesting_user_id)
        if account is None:
            raise ValueError(f"Account with ID {account_id} does not exist.")
        result = account.deposit(amount)
        AccountsRepository._save(account)
        return account, result

    @staticmethod
    def withdraw(account_id, amount, requesting_user_id=None):
        account = AccountsRepository.get_account_by_id(account_id, requesting_user_id)
        if account is None:
            raise ValueError(f"Account with ID {account_id} does not exist.")
        result = account.withdraw(amount)
        AccountsRepository._save(account)
        return account, result

    @staticmethod
    def delete_account(account_id, requesting_user_id=None):
        if not account_id:
            raise ValueError("Account ID must be provided for deletion.")

        collection = get_database().accounts
        query = {"account_id": account_id}
        if requesting_user_id is not None:
            query["owner_id"] = requesting_user_id
        result = collection.delete_one(query)
        return result.deleted_count > 0

    @staticmethod
    def delete_accounts_by_branch(branch_code):
        # Cascade for BranchesService.delete_branch: an account can't exist
        # without a branch (branch_code is required at creation), so a
        # deleted branch's accounts are hard-deleted rather than orphaned.
        if not branch_code:
            raise ValueError("Branch code must be provided.")

        collection = get_database().accounts
        result = collection.delete_many({"branch_code": branch_code})
        return result.deleted_count

    @staticmethod
    def set_status(account_id, status: AccountStatus, requesting_user_id=None):
        account = AccountsRepository.get_account_by_id(account_id, requesting_user_id)
        if account is None:
            raise ValueError(f"Account with ID {account_id} does not exist.")
        if status == AccountStatus.ACTIVE:
            account.reactivate_account()
        else:
            account.deactivate_account()
        AccountsRepository._save(account)
        return account

    @staticmethod
    def transfer_funds(source_account_id, target_account_id, amount, requesting_user_id=None):
        if not source_account_id or not target_account_id:
            raise ValueError("Both source and target account IDs must be provided.")
        if source_account_id == target_account_id:
            raise ValueError("Cannot transfer to the same account.")
        if amount <= 0:
            raise ValueError("Transfer amount must be positive.")

        source_account = AccountsRepository.get_account_by_id(source_account_id)
        target_account = AccountsRepository.get_account_by_id(target_account_id)

        if source_account is None:
            raise ValueError(f"Source account with ID {source_account_id} does not exist.")
        if target_account is None:
            raise ValueError(f"Target account with ID {target_account_id} does not exist.")

        if requesting_user_id is not None and source_account.get_owner_id() != requesting_user_id:
            # You can only ever move money OUT of your own account (moving
            # money INTO someone else's account is fine and intentionally
            # not restricted here).
            raise PermissionError("You do not have permission to transfer from this account.")

        result = source_account.transfer(amount, target_account)
        AccountsRepository._save(source_account)
        AccountsRepository._save(target_account)
        return result
