from Services.AccountsService import AccountsService

class AccountsController:
    def __init__(self):
        self.accounts_service = AccountsService()

    def get_all_accounts(self):
        return self.accounts_service.get_all_accounts()
    
    def get_account_by_id(self, account_id):
        return self.accounts_service.get_account_by_id(account_id)

    def create_account(self, account_data):
        return self.accounts_service.create_account(account_data)

    def update_account(self, account_id, account_data):
        return self.accounts_service.update_account(account_id, account_data)

    def delete_account(self, account_id):
        return self.accounts_service.delete_account(account_id)

    def transfer_funds(self, from_account_id, to_account_id, amount):
        return self.accounts_service.transfer_funds(from_account_id, to_account_id, amount)