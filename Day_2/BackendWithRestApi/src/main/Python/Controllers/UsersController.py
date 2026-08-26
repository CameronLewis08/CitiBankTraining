"""
User Controller for the Banking Domain REST API:
    Thin pass-through to UsersService, mirroring the existing Controller
    pattern (no HTTP concerns here - that's all in app.py).
"""

from Services.UsersService import UsersService


class UsersController:
    def __init__(self):
        self.users_service = UsersService()

    def get_all_users(self, requesting_user):
        return self.users_service.get_all_users(requesting_user)

    def get_user_by_id(self, user_id):
        return self.users_service.get_user_by_id(user_id)

    def create_user(self, requesting_user, user_data):
        return self.users_service.create_user(requesting_user, user_data)

    def update_user(self, requesting_user, user_id, user_data):
        return self.users_service.update_user(requesting_user, user_id, user_data)

    def delete_user(self, requesting_user, user_id):
        return self.users_service.delete_user(requesting_user, user_id)

    def login(self, email, password):
        return self.users_service.login(email, password)

    def search_users_by_branch(self, requesting_user, branch_code, role=None, name=None):
        return self.users_service.search_users_by_branch(requesting_user, branch_code, role, name)
