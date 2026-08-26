"""
Database connection helper for the Banking Domain REST API:
    Opens a single shared MongoClient using a connection string from the
    MONGO_URI environment variable, and exposes the target database.
"""

import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

_client = None


def get_database():
    global _client
    db_name = os.environ.get("MONGO_DB_NAME", "banking")

    if _client is None:
        uri = os.environ.get("MONGO_URI")
        if not uri:
            raise RuntimeError(
                "MONGO_URI environment variable is not set. "
                "Copy your Atlas connection string into it before running."
            )
        _client = MongoClient(uri)

        customers_collection = _client[db_name].customers
        customers_collection.create_index("customer_id", unique=True)
        customers_collection.create_index("email", unique=True)

        accounts_collection = _client[db_name].accounts
        accounts_collection.create_index("account_id", unique=True)

    return _client[db_name]

