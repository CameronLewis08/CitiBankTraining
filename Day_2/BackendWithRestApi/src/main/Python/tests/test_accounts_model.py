import pytest

from Models.Accounts import CheckingAccount, SavingsAccount, build_account
from Utilities.Status import AccountType, AccountStatus, OutcomeStatus


def test_checking_account_allows_overdraft_within_limit():
    account = CheckingAccount("ACC-1", 1, 100.0, "BR001")
    result = account.withdraw(600.0)
    assert result["status"] == OutcomeStatus.SUCCESS.value
    assert account.get_balance() == -500.0


def test_checking_account_rejects_overdraft_beyond_limit():
    account = CheckingAccount("ACC-1", 1, 100.0, "BR001")
    result = account.withdraw(601.0)
    assert result["status"] == OutcomeStatus.FAILURE.value
    assert account.get_balance() == 100.0


def test_savings_account_cannot_go_negative():
    account = SavingsAccount("ACC-2", 1, 100.0, "BR001")
    result = account.withdraw(150.0)
    assert result["status"] == OutcomeStatus.FAILURE.value
    assert account.get_balance() == 100.0


def test_savings_account_withdraw_within_balance_succeeds():
    account = SavingsAccount("ACC-2", 1, 100.0, "BR001")
    result = account.withdraw(50.0)
    assert result["status"] == OutcomeStatus.SUCCESS.value
    assert account.get_balance() == 50.0


def test_deposit_and_withdraw_recorded_in_transaction_history():
    account = SavingsAccount("ACC-2", 1, 100.0, "BR001")
    account.deposit(20.0)
    account.withdraw(10.0)
    history = account.get_transaction_history()
    assert [entry["type"] for entry in history] == ["deposit", "withdrawal"]


def test_deposit_fails_on_inactive_account():
    account = SavingsAccount("ACC-2", 1, 100.0, "BR001")
    account.deactivate_account()
    result = account.deposit(10.0)
    assert result["status"] == OutcomeStatus.FAILURE.value
    assert account.get_balance() == 100.0


def test_reactivate_allows_deposit_again():
    account = SavingsAccount("ACC-2", 1, 100.0, "BR001")
    account.deactivate_account()
    account.reactivate_account()
    result = account.deposit(10.0)
    assert result["status"] == OutcomeStatus.SUCCESS.value


def test_transfer_moves_balance_between_accounts():
    source = CheckingAccount("ACC-1", 1, 200.0, "BR001")
    target = SavingsAccount("ACC-2", 2, 50.0, "BR001")
    result = source.transfer(100.0, target)
    assert result["status"] == OutcomeStatus.SUCCESS.value
    assert source.get_balance() == 100.0
    assert target.get_balance() == 150.0


def test_build_account_checking():
    account = build_account(AccountType.CHECKING, "ACC-1", 1, 100.0, "BR001")
    assert isinstance(account, CheckingAccount)
    assert account.get_account_type() == AccountType.CHECKING


def test_build_account_savings():
    account = build_account(AccountType.SAVINGS, "ACC-2", 1, 100.0, "BR001")
    assert isinstance(account, SavingsAccount)


def test_build_account_unknown_type_raises():
    with pytest.raises(ValueError):
        build_account("Bogus", "ACC-3", 1, 100.0, "BR001")


def test_to_dict_shape():
    account = CheckingAccount("ACC-1", 1, 100.0, "BR001")
    account.deposit(10.0)
    data = account.to_dict()
    assert data["account_id"] == "ACC-1"
    assert data["owner_id"] == 1
    assert data["balance"] == 110.0
    assert data["branch_code"] == "BR001"
    assert data["account_type"] == "Checking"
    assert data["status"] == "active"
    assert len(data["transaction_history"]) == 1
