"""
Account Controller for the Banking Domain REST API:
    Thin pass-through to AccountsService.
"""

from Services.AccountsService import AccountsService


class AccountsController:
    def __init__(self):
        self.accounts_service = AccountsService()

    def get_all_accounts(self, requesting_user, owner_id=None):
        return self.accounts_service.get_all_accounts(requesting_user, owner_id)

    def get_account_by_id(self, requesting_user, account_id):
        return self.accounts_service.get_account_by_id(requesting_user, account_id)

    def create_account(self, requesting_user, account_data):
        return self.accounts_service.create_account(requesting_user, account_data)

    def deposit(self, requesting_user, account_id, amount):
        return self.accounts_service.deposit(requesting_user, account_id, amount)

    def withdraw(self, requesting_user, account_id, amount):
        return self.accounts_service.withdraw(requesting_user, account_id, amount)

    def delete_account(self, requesting_user, account_id):
        return self.accounts_service.delete_account(requesting_user, account_id)

    def set_status(self, requesting_user, account_id, status):
        return self.accounts_service.set_status(requesting_user, account_id, status)

    def transfer_funds(self, requesting_user, from_account_id, to_account_id, amount):
        return self.accounts_service.transfer_funds(requesting_user, from_account_id, to_account_id, amount)