"""
Customer Controller for the Banking Domain REST API:
    This module defines the CustomerController class, which handles the HTTP requests and responses for customer-related operations.
    It includes methods for creating, reading, updating, and deleting customer records.
"""

from Services.CustomersService import CustomerService

class CustomerController:
    def __init__(self):
        self.customer_service = CustomerService()

    def get_all_customers(self):
        return self.customer_service.get_all_customers()

    def get_customer_by_id(self, customer_id):
        return self.customer_service.get_customer_by_id(customer_id)

    def create_customer(self, customer_data):
        return self.customer_service.create_customer(customer_data)

    def update_customer(self, customer_id, customer_data):
        return self.customer_service.update_customer(customer_id, customer_data)

    def delete_customer(self, customer_id):
        return self.customer_service.delete_customer(customer_id)
    