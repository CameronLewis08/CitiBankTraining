"""
One-time seed script:
    Loads the sample customers and accounts into the MongoDB
    'customers' and 'accounts' collections.
    Run directly: python Utilities/SeedMongo.py
"""

from Utilities.Database import get_database

SAMPLE_CUSTOMERS = [
    {"customer_id": 1, "name": "John Doe", "email": "john.doe@example.com"},
    {"customer_id": 2, "name": "Jane Smith", "email": "Jane.Smith@example.com"},
    {"customer_id": 3, "name": "Bob John", "email": "Bob.Johnson@example.com"},
]

SAMPLE_ACCOUNTS = [
    {"account_id": "ACC-1001", "customer_id": 1, "balance": 500.00},
    {"account_id": "ACC-1002", "customer_id": 2, "balance": 1250.75},
    {"account_id": "ACC-1003", "customer_id": 2, "balance": 300.00},
    {"account_id": "ACC-1004", "customer_id": 3, "balance": 0.00},
]

if __name__ == "__main__":
    customers_collection = get_database().customers
    for customer in SAMPLE_CUSTOMERS:
        customers_collection.update_one(
            {"customer_id": customer["customer_id"]},
            {"$set": customer},
            upsert=True,
        )
    print(f"Seeded {len(SAMPLE_CUSTOMERS)} customers into MongoDB.")

    accounts_collection = get_database().accounts
    for account in SAMPLE_ACCOUNTS:
        accounts_collection.update_one(
            {"account_id": account["account_id"]},
            {"$set": account},
            upsert=True,
        )
    print(f"Seeded {len(SAMPLE_ACCOUNTS)} accounts into MongoDB.")
