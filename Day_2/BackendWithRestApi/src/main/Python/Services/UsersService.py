"""
User Service for the Banking Domain REST API:
    Business logic for users, including role-based permission checks
    ported from Day_1's Bank.create_user/remove_user. Checks happen
    before any Repo/Mongo call so they're unit-testable without a
    database connection.
"""

import bcrypt

from Repos.UsersRepo import UsersRepository
from Utilities.Status import UserRole


class UsersService:
    @staticmethod
    def get_all_users():
        return UsersRepository.get_all_users()

    @staticmethod
    def get_user_by_id(user_id):
        return UsersRepository.get_user_by_id(user_id)

    @staticmethod
    def create_user(requesting_user, user_data):
        if requesting_user.get_role() not in (UserRole.ADMIN, UserRole.MANAGER):
            raise PermissionError("Only Admins and Managers can create users.")

        user_data = dict(user_data)
        password = user_data.pop("password", None)
        if password:
            hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
            user_data["password_hash"] = hashed.decode("utf-8")
        return UsersRepository.create_user(user_data)

    @staticmethod
    def update_user(user_id, user_data):
        return UsersRepository.update_user(user_id, user_data)

    @staticmethod
    def delete_user(requesting_user, user_id):
        if requesting_user.get_role() not in (UserRole.ADMIN, UserRole.MANAGER):
            raise PermissionError("Only Admins and Managers can remove users.")
        return UsersRepository.delete_user(user_id)

    @staticmethod
    def login(email, password):
        user = UsersRepository.get_user_by_email(email)
        if not user or not user.verify_password(password):
            raise ValueError("Invalid email or password.")
        return user
