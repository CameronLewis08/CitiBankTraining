
from Controllers.CustomersController import CustomerController


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

if __name__ == "__main__":
    main()
