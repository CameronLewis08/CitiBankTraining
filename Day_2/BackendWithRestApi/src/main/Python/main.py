
from Controllers.CustomersController import CustomerController
from Services.AccountsService import AccountsService


def expect_error(description, action):
    try:
        action()
        print(f"FAIL - {description}: expected a ValueError but none was raised.")
    except ValueError as e:
        print(f"PASS - {description}: {e}")


def main():
    print("Welcome to the Banking Domain Console Application!")
    # You can add more functionality here, such as a menu for user interaction.
    controller = CustomerController()
    # Example usage of the controller
    all_customers = controller.get_all_customers()
    print("All Customers:")
    for customer in all_customers:
        print(f"ID: {customer.get_customer_id()}, Name: {customer.get_name()}, Email: {customer.get_email()}")

    print("\nGet Customer by ID (1):")
    customer = controller.get_customer_by_id(1)
    if customer:
        print(f"ID: {customer.get_customer_id()}, Name: {customer.get_name()}, Email: {customer.get_email()}")
    else:
        print("Customer not found.")

    print("\nCreate Customer (4):")
    new_customer = controller.create_customer({"customer_id": 4, "name": "Alice Walker", "email": "alice.walker@example.com"})
    print(f"ID: {new_customer.get_customer_id()}, Name: {new_customer.get_name()}, Email: {new_customer.get_email()}")

    print("\nUpdate Customer (4):")
    updated_customer = controller.update_customer(4, {"name": "Alice Walker-Smith"})
    print(f"ID: {updated_customer.get_customer_id()}, Name: {updated_customer.get_name()}, Email: {updated_customer.get_email()}")

    print("\nDelete Customer (4):")
    deleted = controller.delete_customer(4)
    print(f"Deleted: {deleted}")

    print("\nGet Customer by ID (4) after delete:")
    customer = controller.get_customer_by_id(4)
    if customer:
        print(f"ID: {customer.get_customer_id()}, Name: {customer.get_name()}, Email: {customer.get_email()}")
    else:
        print("Customer not found.")

    print("\nEdge cases:")

    expect_error(
        "create with duplicate customer_id",
        lambda: controller.create_customer({"customer_id": 1, "name": "Dup ID", "email": "dup.id@example.com"}),
    )

    expect_error(
        "create with duplicate email",
        lambda: controller.create_customer({"customer_id": 99, "name": "Dup Email", "email": "john.doe@example.com"}),
    )

    expect_error(
        "create with missing fields",
        lambda: controller.create_customer({"customer_id": 100, "name": "No Email"}),
    )

    expect_error(
        "update a customer that does not exist",
        lambda: controller.update_customer(999, {"name": "Ghost"}),
    )

    expect_error(
        "update with mismatched customer_id in payload",
        lambda: controller.update_customer(1, {"customer_id": 2, "name": "Mismatch"}),
    )

    expect_error(
        "delete a customer that does not exist",
        lambda: controller.delete_customer(999),
    )

    expect_error(
        "get_customer_by_id with falsy id",
        lambda: controller.get_customer_by_id(0),
    )

    print("\n--- Accounts ---")

    print("\nAll Accounts:")
    all_accounts = AccountsService.get_all_accounts()
    for account in all_accounts:
        print(f"ID: {account.get_account_id()}, Customer ID: {account.get_customer_id()}, Balance: {account.get_balance()}")

    print("\nGet Account by ID (ACC-1001):")
    account = AccountsService.get_account_by_id("ACC-1001")
    if account:
        print(f"ID: {account.get_account_id()}, Customer ID: {account.get_customer_id()}, Balance: {account.get_balance()}")
    else:
        print("Account not found.")

    print("\nCreate Account (ACC-2001):")
    new_account = AccountsService.create_account({"account_id": "ACC-2001", "customer_id": 1, "balance": 100.00})
    print(f"ID: {new_account.get_account_id()}, Customer ID: {new_account.get_customer_id()}, Balance: {new_account.get_balance()}")

    print("\nUpdate Account (ACC-2001):")
    updated_account = AccountsService.update_account("ACC-2001", {"customer_id": 1, "balance": 250.00})
    print(f"ID: {updated_account.get_account_id()}, Customer ID: {updated_account.get_customer_id()}, Balance: {updated_account.get_balance()}")

    print("\nDelete Account (ACC-2001):")
    deleted_account = AccountsService.delete_account("ACC-2001")
    print(f"Deleted: {deleted_account}")

    print("\nGet Account by ID (ACC-2001) after delete:")
    account = AccountsService.get_account_by_id("ACC-2001")
    if account:
        print(f"ID: {account.get_account_id()}, Customer ID: {account.get_customer_id()}, Balance: {account.get_balance()}")
    else:
        print("Account not found.")

    print("\nTransfer (ACC-1001 -> ACC-1002, 100.00):")
    AccountsService.transfer_funds("ACC-1001", "ACC-1002", 100.00)
    source_account = AccountsService.get_account_by_id("ACC-1001")
    target_account = AccountsService.get_account_by_id("ACC-1002")
    print(f"Source balance: {source_account.get_balance()}, Target balance: {target_account.get_balance()}")

    print("\nAccount edge cases:")

    expect_error(
        "create account with negative balance",
        lambda: AccountsService.create_account({"account_id": "ACC-3001", "customer_id": 1, "balance": -50.00}),
    )

    expect_error(
        "create account with missing fields",
        lambda: AccountsService.create_account({"account_id": "ACC-3002"}),
    )

    expect_error(
        "transfer with insufficient balance",
        lambda: AccountsService.transfer_funds("ACC-1003", "ACC-1004", 100000.00),
    )

    expect_error(
        "transfer with non-positive amount",
        lambda: AccountsService.transfer_funds("ACC-1003", "ACC-1004", 0),
    )

    expect_error(
        "transfer from a nonexistent source account",
        lambda: AccountsService.transfer_funds("ACC-9999", "ACC-1004", 10.00),
    )

    expect_error(
        "transfer to a nonexistent target account",
        lambda: AccountsService.transfer_funds("ACC-1003", "ACC-9999", 10.00),
    )

    expect_error(
        "update an account that does not exist",
        lambda: AccountsService.update_account("ACC-9999", {"customer_id": 1, "balance": 10.00}),
    )

    expect_error(
        "update with mismatched account_id in payload",
        lambda: AccountsService.update_account("ACC-1001", {"account_id": "ACC-9999", "customer_id": 1, "balance": 10.00}),
    )

    expect_error(
        "update account missing customer_id",
        lambda: AccountsService.update_account("ACC-1001", {"balance": 10.00}),
    )

    expect_error(
        "get_account_by_id with falsy id",
        lambda: AccountsService.get_account_by_id(""),
    )

if __name__ == "__main__":
    main()
