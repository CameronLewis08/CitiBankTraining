
"""
Customer Repository for the Banking Domain REST API:
    This module defines the CustomerRepository class, which provides methods for interacting with the customer data in the database.
    It includes methods for creating, reading, updating, and deleting customer records.
"""

from Utilities.Database import get_database
from Models.Customers import Customers
from pymongo.errors import DuplicateKeyError

def _to_customer(doc) -> Customers:
    return Customers(doc["customer_id"], doc["name"], doc["email"])


class CustomerRepository:

    @staticmethod
    def get_all_customers() -> list:
        collection = get_database().customers
        return [_to_customer(doc) for doc in collection.find()]

    @staticmethod
    def get_customer_by_id(customer_id: int) -> Customers:
        if not customer_id:
            raise ValueError("Customer ID must be provided.")
        
        collection = get_database().customers
        doc = collection.find_one({"customer_id": customer_id})
        return _to_customer(doc) if doc else None

    @staticmethod
    def create_customer(customer_data: dict) -> Customers:
        if not customer_data.get("customer_id") or not customer_data.get("name") or not customer_data.get("email"):
            raise ValueError("Customer data must include 'customer_id', 'name', and 'email' fields.")
        
        collection = get_database().customers

        try:
            collection.insert_one(customer_data)
        except DuplicateKeyError as e:
            if "email" in e.details.get("keyPattern", {}):
                raise ValueError(f"Customer with email {customer_data['email']} already exists.")
            raise ValueError(f"Customer with ID {customer_data['customer_id']} already exists.")
        
        return CustomerRepository.get_customer_by_id(customer_data["customer_id"])

    @staticmethod
    def update_customer(customer_id: int, customer_data: dict) -> Customers:
        if not customer_id:
            raise ValueError("Customer ID must be provided for update.")
        
        if not customer_data or (not customer_data.get("name") and not customer_data.get("email")):
            raise ValueError("Customer data must not be empty and must include 'name' or 'email' fields for update.")
        
        if "customer_id" in customer_data and customer_data["customer_id"] != customer_id:
            raise ValueError("Customer ID in the data does not match the provided customer ID.")

        customer = CustomerRepository.get_customer_by_id(customer_id)
        if customer is None:
            raise ValueError(f"Customer with ID {customer_id} does not exist.")

        if "name" in customer_data:
            customer.set_name(customer_data["name"])
        if "email" in customer_data:
            customer.set_email(customer_data["email"])

        collection = get_database().customers
        collection.update_one({"customer_id": customer_id}, {"$set": customer.to_dict()})

        return customer

    @staticmethod
    def delete_customer(customer_id: int) -> bool:
        if not customer_id:
            raise ValueError("Customer ID must be provided for deletion.")
        
        collection = get_database().customers
        result = collection.delete_one({"customer_id": customer_id})
        if result.deleted_count == 0:
            raise ValueError(f"Customer with ID {customer_id} does not exist.")
        
        return True