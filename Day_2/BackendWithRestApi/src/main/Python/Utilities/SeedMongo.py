"""
One-time seed script:
    Loads sample users (one per role), branches, and accounts into
    MongoDB. Mirrors Day_1's seed_data.py structure, adapted to
    Day_2's email-based login.
    Run directly: python Utilities/SeedMongo.py
"""

import bcrypt

from Utilities.Database import get_database

SAMPLE_PASSWORD = "password123"

SAMPLE_USERS = [
    {"user_id": 1, "name": "Alex Admin", "email": "admin@citibank.com", "role": "Admin", "branch_code": None},
    {"user_id": 2, "name": "Jamie Jones", "email": "mgr.jones@citibank.com", "role": "Manager", "branch_code": "BR001"},
    {"user_id": 3, "name": "Lee Park", "email": "mgr.lee@citibank.com", "role": "Manager", "branch_code": "BR002"},
    {"user_id": 4, "name": "Amy Staff", "email": "staff.amy@citibank.com", "role": "Staff", "branch_code": "BR001"},
    {"user_id": 5, "name": "Ravi Staff", "email": "staff.ravi@citibank.com", "role": "Staff", "branch_code": "BR002"},
    {"user_id": 6, "name": "Bob Customer", "email": "bob.customer@example.com", "role": "Customer", "branch_code": "BR001"},
    {"user_id": 7, "name": "Amy Customer", "email": "amy.customer@example.com", "role": "Customer", "branch_code": "BR002"},
]

SAMPLE_BRANCHES = [
    {"branch_code": "BR001", "location": "Downtown Chicago", "manager_id": 2, "staff_list": [4]},
    {"branch_code": "BR002", "location": "Uptown Chicago", "manager_id": 3, "staff_list": [5]},
]

SAMPLE_ACCOUNTS = [
    {"account_id": "ACC-1001", "owner_id": 6, "balance": 1500.00, "branch_code": "BR001",
     "account_type": "Checking", "status": "active", "transaction_history": []},
    {"account_id": "ACC-1002", "owner_id": 6, "balance": 5000.00, "branch_code": "BR001",
     "account_type": "Savings", "status": "active", "transaction_history": []},
    {"account_id": "ACC-2001", "owner_id": 7, "balance": 750.00, "branch_code": "BR002",
     "account_type": "Checking", "status": "active", "transaction_history": []},
]

if __name__ == "__main__":
    users_collection = get_database().users
    password_hash = bcrypt.hashpw(SAMPLE_PASSWORD.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    for user in SAMPLE_USERS:
        user_doc = dict(user)
        user_doc["password_hash"] = password_hash
        users_collection.update_one({"user_id": user_doc["user_id"]}, {"$set": user_doc}, upsert=True)
    print(f"Seeded {len(SAMPLE_USERS)} users into MongoDB (password: '{SAMPLE_PASSWORD}').")

    # Bump the user_id counter to at least the highest seeded ID, so the
    # first auto-assigned signup ID (UsersRepository.get_next_user_id) can
    # never collide with a seeded user. Only raises the counter, never
    # lowers it, so re-running the seed script is safe.
    counters_collection = get_database().counters
    max_seeded_id = max(user["user_id"] for user in SAMPLE_USERS)
    counters_collection.update_one(
        {"_id": "user_id", "seq": {"$lt": max_seeded_id}},
        {"$set": {"seq": max_seeded_id}},
        upsert=True,
    )

    branches_collection = get_database().branches
    for branch in SAMPLE_BRANCHES:
        branches_collection.update_one({"branch_code": branch["branch_code"]}, {"$set": branch}, upsert=True)
    print(f"Seeded {len(SAMPLE_BRANCHES)} branches into MongoDB.")

    accounts_collection = get_database().accounts
    for account in SAMPLE_ACCOUNTS:
        accounts_collection.update_one({"account_id": account["account_id"]}, {"$set": account}, upsert=True)
    print(f"Seeded {len(SAMPLE_ACCOUNTS)} accounts into MongoDB.")

    print("\nSeed accounts (email / password / role / branch):")
    for user in SAMPLE_USERS:
        branch_label = user["branch_code"] or "-"
        print(f"  {user['email']:<28} / {SAMPLE_PASSWORD} ({user['role']}, {branch_label})")
