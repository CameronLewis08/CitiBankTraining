"""
Branch Service for the Banking Domain REST API:
    Permission checks ported from Day_1's Bank.create_branch/remove_branch/
    get_branch_codes, checked before any Repo/Mongo call.
"""

from Repos.BranchesRepo import BranchesRepository
from Utilities.Status import UserRole


class BranchesService:
    @staticmethod
    def get_all_branches(requesting_user):
        if requesting_user.get_role() == UserRole.CUSTOMER:
            raise PermissionError("Only Staff can view all branch codes.")
        return BranchesRepository.get_all_branches()

    @staticmethod
    def get_branch_by_code(branch_code):
        return BranchesRepository.get_branch_by_code(branch_code)

    @staticmethod
    def create_branch(requesting_user, branch_data):
        if requesting_user.get_role() != UserRole.ADMIN:
            raise PermissionError("Only Admins can create branches.")
        return BranchesRepository.create_branch(branch_data)

    @staticmethod
    def update_branch(requesting_user, branch_code, branch_data):
        if requesting_user.get_role() != UserRole.ADMIN:
            raise PermissionError("Only Admins can update branches.")
        return BranchesRepository.update_branch(branch_code, branch_data)

    @staticmethod
    def delete_branch(requesting_user, branch_code):
        if requesting_user.get_role() != UserRole.ADMIN:
            raise PermissionError("Only Admins can remove branches.")
        return BranchesRepository.delete_branch(branch_code)
