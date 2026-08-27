"""
Account Service for the Banking Domain REST API:
    Permission checks ported from Day_1's Bank.create_account/
    remove_account, checked before any Repo/Mongo call.
"""

import secrets

from Repos.AccountsRepo import AccountsRepository
from Repos.UsersRepo import UsersRepository
from Utilities.Status import UserRole, AccountType, AccountStatus


class AccountsService:
    @staticmethod
    def get_all_accounts(requesting_user, owner_id=None, skip=0, limit=None, search=None):
        if requesting_user.get_role() == UserRole.CUSTOMER:
            return AccountsRepository.get_all_accounts(
                owner_id=requesting_user.get_user_id(), skip=skip, limit=limit, search=search)
        if requesting_user.get_role() in (UserRole.STAFF, UserRole.MANAGER):
            if owner_id is None:
                return AccountsRepository.get_accounts_by_branch(
                    requesting_user.get_branch_code(), skip=skip, limit=limit, search=search)
            target_user = UsersRepository.get_user_by_id(owner_id)
            if target_user is None or target_user.get_branch_code() != requesting_user.get_branch_code():
                raise PermissionError("You can only view accounts for customers in your own branch.")
            return AccountsRepository.get_all_accounts(owner_id=owner_id, skip=skip, limit=limit, search=search)
        # Admin
        if owner_id is None:
            return AccountsRepository.get_all_accounts(skip=skip, limit=limit, search=search)
        return AccountsRepository.get_all_accounts(owner_id=owner_id, skip=skip, limit=limit, search=search)

    @staticmethod
    def get_account_by_id(requesting_user, account_id):
        if requesting_user.get_role() == UserRole.CUSTOMER:
            return AccountsRepository.get_account_by_id(account_id, requesting_user.get_user_id())
        account = AccountsRepository.get_account_by_id(account_id)
        if account is None:
            return None
        if requesting_user.get_role() in (UserRole.STAFF, UserRole.MANAGER):
            if account.get_branch_code() != requesting_user.get_branch_code():
                raise PermissionError("You can only view accounts in your own branch.")
        return account

    @staticmethod
    def create_account(requesting_user, account_data):
        account_data = dict(account_data)

        if requesting_user.get_role() == UserRole.CUSTOMER:
            # Self-service: customers can only ever open accounts for
            # themselves, regardless of what owner_id they send.
            account_data["owner_id"] = requesting_user.get_user_id()

        if not account_data.get("account_id"):
            account_data["account_id"] = AccountsService._generate_account_id()

        owner_id = account_data.get("owner_id")
        # Checked before creating the account, so this reflects whether it's
        # the owner's *first* account, not whether they have zero now.
        is_first_account = owner_id is not None and not AccountsRepository.get_all_accounts(owner_id=owner_id)

        account = AccountsRepository.create_account(account_data)

        if is_first_account:
            owner = UsersRepository.get_user_by_id(owner_id)
            # Only Customers get an auto-assigned home branch this way -
            # Staff/Manager/Admin branches are an explicit Admin decision,
            # never inferred from an account they happen to open.
            if owner is not None and owner.get_role() == UserRole.CUSTOMER:
                UsersRepository.assign_branch_code(owner_id, account.get_branch_code())

        return account

    @staticmethod
    def _generate_account_id():
        for _ in range(5):
            candidate = f"ACC-{secrets.token_hex(4)}"
            if AccountsRepository.get_account_by_id(candidate) is None:
                return candidate
        raise ValueError("Could not generate a unique account ID; please try again.")

    @staticmethod
    def deposit(requesting_user, account_id, amount):
        if requesting_user.get_role() in (UserRole.ADMIN, UserRole.MANAGER, UserRole.STAFF):
            return AccountsRepository.deposit(account_id, amount)
        owned_account = AccountsRepository.get_account_by_id(account_id, requesting_user.get_user_id())
        if owned_account is None:
            raise PermissionError("You do not have permission to deposit on this account.")
        return AccountsRepository.deposit(account_id, amount, requesting_user.get_user_id())

    @staticmethod
    def withdraw(requesting_user, account_id, amount):
        if requesting_user.get_role() in (UserRole.ADMIN, UserRole.MANAGER, UserRole.STAFF):
            return AccountsRepository.withdraw(account_id, amount)
        owned_account = AccountsRepository.get_account_by_id(account_id, requesting_user.get_user_id())
        if owned_account is None:
            raise PermissionError("You do not have permission to withdraw on this account.")
        return AccountsRepository.withdraw(account_id, amount, requesting_user.get_user_id())

    @staticmethod
    def delete_account(requesting_user, account_id):
        if requesting_user.get_role() not in (UserRole.ADMIN, UserRole.MANAGER, UserRole.STAFF):
            raise PermissionError("Only Admins, Managers, and Staff can remove accounts.")
        return AccountsRepository.delete_account(account_id)

    @staticmethod
    def set_status(requesting_user, account_id, status: AccountStatus):
        if requesting_user.get_role() not in (UserRole.ADMIN, UserRole.MANAGER, UserRole.STAFF):
            raise PermissionError("Only Admins, Managers, and Staff can change account status.")
        return AccountsRepository.set_status(account_id, status)

    @staticmethod
    def search_accounts_by_branch(requesting_user, branch_code, account_type=None, status=None):
        if requesting_user.get_role() != UserRole.ADMIN:
            raise PermissionError("Only Admins can search accounts by branch.")
        resolved_type = AccountType(account_type).value if account_type is not None else None
        resolved_status = AccountStatus(status).value if status is not None else None
        return AccountsRepository.search_accounts_by_branch(branch_code, resolved_type, resolved_status)

    @staticmethod
    def transfer_funds(requesting_user, from_account_id, to_account_id, amount):
        if requesting_user.get_role() in (UserRole.ADMIN, UserRole.MANAGER, UserRole.STAFF):
            return AccountsRepository.transfer_funds(from_account_id, to_account_id, amount)
        return AccountsRepository.transfer_funds(from_account_id, to_account_id, amount, requesting_user.get_user_id())