from Repos.AccountsRepo import AccountsRepository

class AccountsService:
    @staticmethod
    def get_all_accounts():
        return AccountsRepository.get_all_accounts()
    
    @staticmethod
    def get_account_by_id(account_id):
        return AccountsRepository.get_account_by_id(account_id)

    @staticmethod
    def create_account(account_data):
        return AccountsRepository.create_account(account_data)

    @staticmethod
    def update_account(account_id, account_data):
        return AccountsRepository.update_account(account_id, account_data)

    @staticmethod
    def delete_account(account_id):
        return AccountsRepository.delete_account(account_id)

    @staticmethod
    def transfer_funds(from_account_id, to_account_id, amount):
        return AccountsRepository.transfer_funds(from_account_id, to_account_id, amount)