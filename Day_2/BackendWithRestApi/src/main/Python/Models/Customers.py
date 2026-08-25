"""
Customer Model for the Banking Domain REST API:
    This module defines the Customer class, which represents a customer in the banking domain. The Customer class contains attributes such as customer ID, name, email, and account information. It also includes methods for customer management.
    This module should be used in conjunction with other modules in the banking domain to provide a complete banking application experience.
"""

class Customers:
    def __init__(self, customer_id, name, email):
        self.customer_id = customer_id
        self.name = name
        self.email = email

    def get_customer_id(self):
        return self.customer_id

    def get_name(self):
        return self.name

    def get_email(self):
        return self.email

    def set_customer_id(self, new_customer_id):
        if not new_customer_id:
            raise ValueError("Customer ID cannot be empty.")
        else:
            self.customer_id = new_customer_id
            return f"Customer ID updated to {new_customer_id}."

    def set_name(self, new_name):
        if not new_name:
            raise ValueError("Name cannot be empty.")
        else:
            self.name = new_name
            return f"Name updated to {new_name}."
        
    def set_email(self, new_email):
        if not new_email:
            raise ValueError("Email cannot be empty")
        elif "@" not in new_email or "." not in new_email:
            raise ValueError("Invalid email format missing '@' or '.'")
        else:
            self.email = new_email
            return f"Email updated to {new_email}."

    def __repr__(self):
        return f"Customer ID: {self.customer_id}, Name: {self.name}, Email: {self.email}"
        