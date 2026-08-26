"""
User Repository for the Banking Domain REST API:
    CRUD against the 'users' MongoDB collection. Replaces CustomersRepo -
    same pattern (duplicate-key -> ValueError translation), renamed
    customer_id -> user_id and with a role/branch_code field.
"""

from Utilities.Database import get_database
from Models.Users import Users
from pymongo.errors import DuplicateKeyError


def _to_user(doc) -> Users:
    return Users(
        doc["user_id"], doc["name"], doc["email"], doc["role"],
        branch_code=doc.get("branch_code"), password_hash=doc.get("password_hash"),
    )


class UsersRepository:

    @staticmethod
    def get_all_users() -> list:
        collection = get_database().users
        return [_to_user(doc) for doc in collection.find()]

    @staticmethod
    def get_user_by_id(user_id: int) -> Users:
        if not user_id:
            raise ValueError("User ID must be provided.")

        collection = get_database().users
        doc = collection.find_one({"user_id": user_id})
        return _to_user(doc) if doc else None

    @staticmethod
    def get_user_by_email(email: str) -> Users:
        if not email:
            raise ValueError("Email must be provided.")

        collection = get_database().users
        doc = collection.find_one({"email": email})
        return _to_user(doc) if doc else None

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
    def update_user(user_id: int, user_data: dict) -> Users:
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
            user.branch_code = user_data["branch_code"]

        collection = get_database().users
        try:
            collection.update_one({"user_id": user_id}, {"$set": user.to_dict()})
        except DuplicateKeyError:
            raise ValueError(f"User with email {user_data['email']} already exists.")

        return user

    @staticmethod
    def delete_user(user_id: int) -> bool:
        if not user_id:
            raise ValueError("User ID must be provided for deletion.")

        collection = get_database().users
        result = collection.delete_one({"user_id": user_id})
        if result.deleted_count == 0:
            raise ValueError(f"User with ID {user_id} does not exist.")

        return True
