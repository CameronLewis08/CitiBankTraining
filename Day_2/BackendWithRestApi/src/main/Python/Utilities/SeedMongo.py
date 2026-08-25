"""
One-time seed script:
    Loads the sample customers into the MongoDB 'customers' collection.
    Run directly: python Utilities/SeedMongo.py
"""

from Utilities.Database import get_database

SAMPLE_CUSTOMERS = [
    {"customer_id": 1, "name": "John Doe", "email": "john.doe@example.com"},
    {"customer_id": 2, "name": "Jane Smith", "email": "Jane.Smith@example.com"},
    {"customer_id": 3, "name": "Bob John", "email": "Bob.Johnson@example.com"},
]

if __name__ == "__main__":
    collection = get_database().customers
    for customer in SAMPLE_CUSTOMERS:
        collection.update_one(
            {"customer_id": customer["customer_id"]},
            {"$set": customer},
            upsert=True,
        )
    print(f"Seeded {len(SAMPLE_CUSTOMERS)} customers into MongoDB.")
