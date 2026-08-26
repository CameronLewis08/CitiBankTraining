"""
Console smoke-test script for the Banking Domain REST API layers:
    Exercises the Controller/Service layer directly (Users, Branches,
    Accounts) against the seeded MongoDB data, printing pass/fail for a
    set of edge cases. Not an automated test suite - see src/main/Python/tests/
    for pytest coverage of the Service-layer permission checks.
    Run after Utilities/SeedMongo.py: python main.py
"""

from Controllers.UsersController import UsersController
from Controllers.BranchesController import BranchesController
from Controllers.AccountsController import AccountsController
from Utilities.Status import AccountStatus


def expect_error(description, action, expected_exception=ValueError):
    try:
        action()
        print(f"FAIL - {description}: expected {expected_exception.__name__} but none was raised.")
    except expected_exception as e:
        print(f"PASS - {description}: {e}")


def main():
    print("Banking Domain REST API - console smoke test")
    users = UsersController()
    branches = BranchesController()
    accounts = AccountsController()

    admin = users.login("admin@citibank.com", "password123")
    manager = users.login("mgr.jones@citibank.com", "password123")
    staff = users.login("staff.amy@citibank.com", "password123")
    customer = users.login("bob.customer@example.com", "password123")
    print(f"Logged in as: {admin}, {manager}, {staff}, {customer}")

    print("\n--- Users ---")
    print("All users:", [str(u) for u in users.get_all_users(admin)])

    print("\n--- Branches ---")
    print("All branches (as manager):", [str(b) for b in branches.get_all_branches(manager)])

    print("\n--- Accounts ---")
    bob_accounts = accounts.get_all_accounts(customer)
    print("Bob's accounts:", [str(a) for a in bob_accounts])

    print("\nDeposit 100 into ACC-1001:")
    account, result = accounts.deposit(customer, "ACC-1001", 100.0)
    print(result, "new balance:", account.get_balance())

    print("\nWithdraw 200 from ACC-1001 (Checking, overdraft allowed):")
    account, result = accounts.withdraw(customer, "ACC-1001", 2000.0)
    print(result, "new balance:", account.get_balance())

    print("\nTransfer 50 from ACC-1001 to ACC-1002:")
    print(accounts.transfer_funds(customer, "ACC-1001", "ACC-1002", 50.0))

    print("\nDeactivate ACC-1002 (as staff), then try to deposit:")
    accounts.set_status(staff, "ACC-1002", AccountStatus.INACTIVE)
    account, result = accounts.deposit(staff, "ACC-1002", 10.0)
    print(result)
    accounts.set_status(staff, "ACC-1002", AccountStatus.ACTIVE)

    print("\n--- Edge cases ---")

    expect_error(
        "customer cannot view all branches",
        lambda: branches.get_all_branches(customer),
        expected_exception=PermissionError,
    )

    expect_error(
        "staff cannot create a branch",
        lambda: branches.create_branch(staff, {"branch_code": "BR999", "location": "Nowhere"}),
        expected_exception=PermissionError,
    )

    expect_error(
        "customer cannot create an account",
        lambda: accounts.create_account(customer, {
            "account_id": "ACC-9999", "owner_id": customer.get_user_id(), "balance": 10.0,
            "branch_code": "BR001", "account_type": "Checking",
        }),
        expected_exception=PermissionError,
    )

    expect_error(
        "staff cannot create a user",
        lambda: users.create_user(staff, {
            "user_id": 999, "name": "Nobody", "email": "nobody@example.com", "role": "Customer",
        }),
        expected_exception=PermissionError,
    )

    expect_error(
        "login with wrong password",
        lambda: users.login("bob.customer@example.com", "wrong-password"),
    )

    expect_error(
        "get account belonging to someone else returns None, not raise",
        lambda: (_ for _ in ()).throw(AssertionError("should not reach here"))
        if accounts.get_account_by_id("ACC-2001", customer.get_user_id()) is not None
        else (_ for _ in ()).throw(ValueError("account correctly hidden from non-owner")),
    )


if __name__ == "__main__":
    main()
