
from Repos.CustomersRepo import CustomerRepository

class CustomerService:
    @staticmethod
    def get_all_customers():
        return CustomerRepository.get_all_customers()
    
    @staticmethod
    def get_customer_by_id(customer_id):
        return CustomerRepository.get_customer_by_id(customer_id)

    @staticmethod
    def create_customer(customer_data):
        return CustomerRepository.create_customer(customer_data)

    @staticmethod
    def update_customer(customer_id, customer_data):
        return CustomerRepository.update_customer(customer_id, customer_data)

    @staticmethod
    def delete_customer(customer_id):
        return CustomerRepository.delete_customer(customer_id)
    
    