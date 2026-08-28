"""
Seed script:
    Wipes the users, branches, accounts, and counters collections, then
    loads sample users (one per role), branches, and accounts into
    MongoDB. Mirrors Day_1's seed_data.py structure, adapted to
    Day_2's email-based login.

    Destructive: this deletes ALL current users/branches/accounts, not
    just the sample ones - any signups or test data created since the
    last seed run are gone after this. That's intentional (it's what
    gives a deterministic clean baseline), not an oversight.

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
    {"user_id": 6, "name": "Jordan Staff", "email": "staff.jordan@citibank.com", "role": "Staff", "branch_code": "BR002"},
    {"user_id": 7, "name": "Bob Customer", "email": "bob.customer@example.com", "role": "Customer", "branch_code": "BR001"},
    {"user_id": 8, "name": "Amy Customer", "email": "amy.customer@example.com", "role": "Customer", "branch_code": "BR002"},
]

SAMPLE_BRANCHES = [
    {"branch_code": "BR001", "location": "Downtown Chicago", "manager_id": 2, "staff_list": [4]},
    {"branch_code": "BR002", "location": "Uptown Chicago", "manager_id": 3, "staff_list": [5, 6]},
]

SAMPLE_ACCOUNTS = [
    {"account_id": "ACC-1001", "owner_id": 7, "balance": 1500.00, "branch_code": "BR001",
     "account_type": "Checking", "status": "active", "transaction_history": []},
    {"account_id": "ACC-1002", "owner_id": 7, "balance": 5000.00, "branch_code": "BR001",
     "account_type": "Savings", "status": "active", "transaction_history": []},
    {"account_id": "ACC-2001", "owner_id": 8, "balance": 750.00, "branch_code": "BR002",
     "account_type": "Checking", "status": "active", "transaction_history": []},
]

if __name__ == "__main__":
    db = get_database()

    # Wipe first, so re-running this always produces the exact same
    # deterministic baseline - not "sample data plus whatever accumulated
    # since the last run."
    deleted_users = db.users.delete_many({}).deleted_count
    deleted_branches = db.branches.delete_many({}).deleted_count
    deleted_accounts = db.accounts.delete_many({}).deleted_count
    db.counters.delete_many({})
    print(
        f"Wiped {deleted_users} users, {deleted_branches} branches, "
        f"{deleted_accounts} accounts, and reset counters."
    )

    users_collection = db.users
    password_hash = bcrypt.hashpw(SAMPLE_PASSWORD.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    for user in SAMPLE_USERS:
        user_doc = dict(user)
        user_doc["password_hash"] = password_hash
        users_collection.insert_one(user_doc)
    print(f"Seeded {len(SAMPLE_USERS)} users into MongoDB (password: '{SAMPLE_PASSWORD}').")

    # Set the user_id counter to exactly the highest seeded ID, so the
    # first auto-assigned signup ID (UsersRepository.get_next_user_id)
    # can't collide with a seeded user. Safe to set unconditionally here
    # since the collections were just wiped - there's nothing higher to
    # preserve.
    counters_collection = db.counters
    max_seeded_id = max(user["user_id"] for user in SAMPLE_USERS)
    counters_collection.update_one(
        {"_id": "user_id"},
        {"$set": {"seq": max_seeded_id}},
        upsert=True,
    )

    branches_collection = db.branches
    for branch in SAMPLE_BRANCHES:
        branches_collection.insert_one(dict(branch))
    print(f"Seeded {len(SAMPLE_BRANCHES)} branches into MongoDB.")

    accounts_collection = db.accounts
    for account in SAMPLE_ACCOUNTS:
        accounts_collection.insert_one(dict(account))
    print(f"Seeded {len(SAMPLE_ACCOUNTS)} accounts into MongoDB.")

    print("\nSeed accounts (email / password / role / branch):")
    for user in SAMPLE_USERS:
        branch_label = user["branch_code"] or "-"
        print(f"  {user['email']:<28} / {SAMPLE_PASSWORD} ({user['role']}, {branch_label})")
