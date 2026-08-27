"""
User Repository for the Banking Domain REST API:
    CRUD against the 'users' MongoDB collection. Replaces CustomersRepo -
    same pattern (duplicate-key -> ValueError translation), renamed
    customer_id -> user_id and with a role/branch_code field.
"""

import re

from Utilities.Database import get_database
from Models.Users import Users
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError


def _to_user(doc) -> Users:
    return Users(
        doc["user_id"], doc["name"], doc["email"], doc["role"],
        branch_code=doc.get("branch_code"), password_hash=doc.get("password_hash"),
    )


class UsersRepository:

    @staticmethod
    def get_all_users(skip=0, limit=None, search=None) -> list:
        collection = get_database().users
        query = {}
        if search:
            pattern = re.escape(search)
            query["$or"] = [
                {"name": {"$regex": pattern, "$options": "i"}},
                {"email": {"$regex": pattern, "$options": "i"}},
                {"branch_code": {"$regex": pattern, "$options": "i"}},
            ]
        cursor = collection.find(query).skip(skip)
        if limit is not None:
            cursor = cursor.limit(limit)
        return [_to_user(doc) for doc in cursor]

    @staticmethod
    def get_user_by_id(user_id: int) -> Users:
        if not user_id:
            raise ValueError("User ID must be provided.")

        collection = get_database().users
        doc = collection.find_one({"user_id": user_id})
        return _to_user(doc) if doc else None

    @staticmethod
    def get_users_by_ids(user_ids: list) -> list:
        # Bulk lookup for enriching another resource's response (e.g.
        # attaching each account's owner name) - one round trip via $in
        # instead of N single-user queries.
        if not user_ids:
            return []
        collection = get_database().users
        return [_to_user(doc) for doc in collection.find({"user_id": {"$in": list(set(user_ids))}})]

    @staticmethod
    def get_user_by_email(email: str) -> Users:
        if not email:
            raise ValueError("Email must be provided.")

        collection = get_database().users
        doc = collection.find_one({"email": email})
        return _to_user(doc) if doc else None

    @staticmethod
    def get_next_user_id() -> int:
        # Atomic Mongo-side counter (findOneAndUpdate + $inc), so concurrent
        # signups can never be handed the same "next" ID - unlike computing
        # max(existing_ids) + 1 in Python, which is a read-then-write race.
        counters = get_database().counters
        doc = counters.find_one_and_update(
            {"_id": "user_id"},
            {"$inc": {"seq": 1}},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
        return doc["seq"]

    @staticmethod
    def create_user(user_data: dict) -> Users:
        required = ("user_id", "name", "email", "role")
        if not all(user_data.get(field) for field in required):
            raise ValueError("User data must include 'user_id', 'name', 'email', and 'role' fields.")

        collection = get_database().users
        try:
            collection.insert_one(user_data)
        except DuplicateKeyError as e:
            if "email" in e.details.get("keyPattern", {}):
                raise ValueError(f"User with email {user_data['email']} already exists.")
            raise ValueError(f"User with ID {user_data['user_id']} already exists.")

        return UsersRepository.get_user_by_id(user_data["user_id"])

    @staticmethod
    def update_user(user_id: int, user_data: dict, requesting_user) -> Users:
        if not user_id:
            raise ValueError("User ID must be provided for update.")
        if not user_data:
            raise ValueError("User data must not be empty.")
        if "user_id" in user_data and user_data["user_id"] != user_id:
            raise ValueError("User ID in the data does not match the provided user ID.")

        user = UsersRepository.get_user_by_id(user_id)
        if user is None:
            raise ValueError(f"User with ID {user_id} does not exist.")

        if "name" in user_data:
            user.set_name(user_data["name"])
        if "email" in user_data:
            user.set_email(user_data["email"])
        if "branch_code" in user_data:
            user.set_branch_code(requesting_user, user_data["branch_code"])

        collection = get_database().users
        try:
            collection.update_one({"user_id": user_id}, {"$set": user.to_dict()})
        except DuplicateKeyError as e:
            if "email" in e.details.get("keyPattern", {}):
                raise ValueError(f"User with email {user_data['email']} already exists.")
            raise ValueError("Update violates a uniqueness constraint.")

        return user

    @staticmethod
    def assign_branch_code(user_id: int, branch_code: str) -> None:
        # Bypasses Users.set_branch_code's permission check on purpose:
        # this is a system-derived side effect (a Customer's first account
        # determines their home branch), not a user-initiated change, so
        # it isn't subject to the Admin-only rule that governs explicit
        # PUT /users/{id} edits (UsersService.update_user).
        collection = get_database().users
        collection.update_one({"user_id": user_id}, {"$set": {"branch_code": branch_code}})

    @staticmethod
    def search_users_by_branch(branch_code, role=None, name=None, skip=0, limit=None, search=None) -> list:
        query = {"branch_code": branch_code}
        if role is not None:
            query["role"] = role
        if name:
            query["name"] = {"$regex": re.escape(name), "$options": "i"}
        if search:
            pattern = re.escape(search)
            query["$or"] = [
                {"name": {"$regex": pattern, "$options": "i"}},
                {"email": {"$regex": pattern, "$options": "i"}},
            ]
        collection = get_database().users
        cursor = collection.find(query).skip(skip)
        if limit is not None:
            cursor = cursor.limit(limit)
        return [_to_user(doc) for doc in cursor]

    @staticmethod
    def delete_user(user_id: int) -> bool:
        if not user_id:
            raise ValueError("User ID must be provided for deletion.")

        collection = get_database().users
        result = collection.delete_one({"user_id": user_id})
        if result.deleted_count == 0:
            raise ValueError(f"User with ID {user_id} does not exist.")

        return True
