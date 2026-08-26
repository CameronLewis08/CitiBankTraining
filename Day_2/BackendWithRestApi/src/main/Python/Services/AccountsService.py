"""
Account Service for the Banking Domain REST API:
    Permission checks ported from Day_1's Bank.create_account/
    remove_account, checked before any Repo/Mongo call.
"""

from Repos.AccountsRepo import AccountsRepository
from Utilities.Status import UserRole, AccountStatus


class AccountsService:
    @staticmethod
    def get_all_accounts(owner_id=None):
        return AccountsRepository.get_all_accounts(owner_id)

    @staticmethod
    def get_account_by_id(account_id, owner_id=None):
        return AccountsRepository.get_account_by_id(account_id, owner_id)

    @staticmethod
    def create_account(requesting_user, account_data):
        if requesting_user.get_role() not in (UserRole.ADMIN, UserRole.MANAGER, UserRole.STAFF):
            raise PermissionError("Only Admins, Managers, and Staff can create accounts.")
        return AccountsRepository.create_account(account_data)

    @staticmethod
    def deposit(account_id, amount, requesting_user_id=None):
        return AccountsRepository.deposit(account_id, amount, requesting_user_id)

    @staticmethod
    def withdraw(account_id, amount, requesting_user_id=None):
        return AccountsRepository.withdraw(account_id, amount, requesting_user_id)

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
    def transfer_funds(from_account_id, to_account_id, amount, requesting_user_id=None):
        return AccountsRepository.transfer_funds(from_account_id, to_account_id, amount, requesting_user_id)