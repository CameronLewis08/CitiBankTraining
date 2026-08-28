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
    def get_all_users(requesting_user, skip=0, limit=None, search=None, role=None):
        resolved_role = UserRole(role).value if role is not None else None
        if requesting_user.get_role() == UserRole.CUSTOMER:
            raise PermissionError("Only Staff can view all users.")
        if requesting_user.get_role() in (UserRole.MANAGER, UserRole.STAFF):
            # Branch-scoped, same as how AccountsService.get_all_accounts
            # already limits Manager/Staff to their own branch.
            return UsersRepository.search_users_by_branch(
                requesting_user.get_branch_code(), role=resolved_role, skip=skip, limit=limit, search=search)
        return UsersRepository.get_all_users(skip=skip, limit=limit, search=search, role=resolved_role)

    @staticmethod
    def get_user_by_id(user_id):
        # Deliberately unauthenticated: app.py's _require_user calls this to
        # resolve *who's asking* from a requesting_user_id in the first
        # place, so it can't itself require a resolved requesting_user -
        # that would be circular. Nothing HTTP-reachable should expose this
        # raw lookup directly; use view_user_profile for that.
        return UsersRepository.get_user_by_id(user_id)

    @staticmethod
    def get_users_by_ids(user_ids):
        # Same "deliberately unauthenticated" reasoning as get_user_by_id:
        # this only enriches a response the caller was already authorized
        # to see (e.g. attaching owner names to an accounts list the
        # requester already has permission to view), not a standalone
        # route of its own.
        return UsersRepository.get_users_by_ids(user_ids)

    @staticmethod
    def view_user_profile(requesting_user, target_user_id):
        # Permission-checked counterpart to get_user_by_id, for the public
        # GET /users/{id} route - without this, user_id being a small
        # sequential integer made every profile enumerable by anyone,
        # logged in or not.
        target_user = UsersRepository.get_user_by_id(target_user_id)
        if target_user is None:
            return None
        if requesting_user.get_role() == UserRole.ADMIN:
            return target_user
        if requesting_user.get_user_id() == target_user_id:
            return target_user
        if requesting_user.get_role() in (UserRole.MANAGER, UserRole.STAFF):
            if target_user.get_branch_code() == requesting_user.get_branch_code():
                return target_user
            raise PermissionError("You can only view users in your own branch.")
        raise PermissionError("You can only view your own profile.")

    @staticmethod
    def create_user(requesting_user, user_data):
        user_data = dict(user_data)

        if requesting_user is None:
            # Public self-signup: no permission check, and any role the
            # caller tried to supply is overwritten - self-signup always
            # produces a Customer, never a privileged role.
            user_data["role"] = UserRole.CUSTOMER.value
        else:
            if requesting_user.get_role() not in (UserRole.ADMIN, UserRole.MANAGER):
                raise PermissionError("Only Admins and Managers can create users.")
            try:
                UserRole(user_data.get("role"))
            except ValueError:
                raise ValueError(f"Invalid role: {user_data.get('role')!r}")

        if not user_data.get("user_id"):
            user_data["user_id"] = UsersRepository.get_next_user_id()

        password = user_data.pop("password", None)
        if password:
            hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
            user_data["password_hash"] = hashed.decode("utf-8")
        return UsersRepository.create_user(user_data)

    @staticmethod
    def update_user(requesting_user, user_id, user_data):
        is_self = requesting_user.get_user_id() == user_id
        if "branch_code" in user_data and requesting_user.get_role() != UserRole.ADMIN:
            # Branch assignment is an Admin-only action, full stop - no
            # self-service exception for any role, including a user
            # changing their own.
            raise PermissionError("Only Admins can change a user's branch code.")
        if not is_self:
            if requesting_user.get_role() not in (UserRole.ADMIN, UserRole.MANAGER):
                raise PermissionError("Only the user themself, or an Admin/Manager, can update a user's profile.")
        return UsersRepository.update_user(user_id, user_data, requesting_user)

    @staticmethod
    def delete_user(requesting_user, user_id):
        if requesting_user.get_role() not in (UserRole.ADMIN, UserRole.MANAGER):
            raise PermissionError("Only Admins and Managers can remove users.")
        return UsersRepository.delete_user(user_id)

    @staticmethod
    def search_users_by_branch(requesting_user, branch_code, role=None, name=None):
        if requesting_user.get_role() != UserRole.ADMIN:
            raise PermissionError("Only Admins can search users by branch.")
        resolved_role = UserRole(role).value if role is not None else None
        return UsersRepository.search_users_by_branch(branch_code, resolved_role, name)

    @staticmethod
    def login(email, password):
        user = UsersRepository.get_user_by_email(email)
        if not user or not user.verify_password(password):
            raise ValueError("Invalid email or password.")
        return user
