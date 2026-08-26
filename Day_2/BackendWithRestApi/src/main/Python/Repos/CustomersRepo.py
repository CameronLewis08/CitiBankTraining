
"""
Customer Repository for the Banking Domain REST API:
    This module defines the CustomerRepository class, which provides methods for interacting with customer data.
    It includes methods for creating, reading, updating, and deleting customer records.
    Storage is an in-memory dictionary (no external database).
"""

from Models.Customers import Customers

_customers: dict[int, Customers] = {
    1: Customers(1, "John Doe", "john.doe@example.com"),
    2: Customers(2, "Jane Smith", "Jane.Smith@example.com"),
    3: Customers(3, "Bob John", "Bob.Johnson@example.com"),
}


class CustomerRepository:

    @staticmethod
    def get_all_customers() -> list:
        return list(_customers.values())

    @staticmethod
    def get_customer_by_id(customer_id: int) -> Customers:
        if not customer_id:
            raise ValueError("Customer ID must be provided.")

        return _customers.get(customer_id)

    @staticmethod
    def create_customer(customer_data: dict) -> Customers:
        if not customer_data.get("customer_id") or not customer_data.get("name") or not customer_data.get("email"):
            raise ValueError("Customer data must include 'customer_id', 'name', and 'email' fields.")

        customer_id = customer_data["customer_id"]
        if customer_id in _customers:
            raise ValueError(f"Customer with ID {customer_id} already exists.")

        if any(customer.get_email() == customer_data["email"] for customer in _customers.values()):
            raise ValueError(f"Customer with email {customer_data['email']} already exists.")

        customer = Customers(customer_id, customer_data["name"], customer_data["email"])
        _customers[customer_id] = customer
        return customer

    @staticmethod
    def update_customer(customer_id: int, customer_data: dict) -> Customers:
        if not customer_id:
            raise ValueError("Customer ID must be provided for update.")

        if not customer_data or (not customer_data.get("name") and not customer_data.get("email")):
            raise ValueError("Customer data must not be empty and must include 'name' or 'email' fields for update.")

        if "customer_id" in customer_data and customer_data["customer_id"] != customer_id:
            raise ValueError("Customer ID in the data does not match the provided customer ID.")

        customer = _customers.get(customer_id)
        if customer is None:
            raise ValueError(f"Customer with ID {customer_id} does not exist.")

        if "name" in customer_data:
            customer.set_name(customer_data["name"])
        if "email" in customer_data:
            customer.set_email(customer_data["email"])

        return customer

    @staticmethod
    def delete_customer(customer_id: int) -> bool:
        if not customer_id:
            raise ValueError("Customer ID must be provided for deletion.")

        if customer_id not in _customers:
            raise ValueError(f"Customer with ID {customer_id} does not exist.")

        del _customers[customer_id]
        return True
