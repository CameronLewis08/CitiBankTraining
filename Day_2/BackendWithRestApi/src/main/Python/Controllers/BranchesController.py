"""
Branch Controller for the Banking Domain REST API:
    Thin pass-through to BranchesService.
"""

from Services.BranchesService import BranchesService


class BranchesController:
    def __init__(self):
        self.branches_service = BranchesService()

    def get_all_branches(self, requesting_user, skip=0, limit=None, search=None):
        return self.branches_service.get_all_branches(requesting_user, skip=skip, limit=limit, search=search)

    def get_branch_by_code(self, branch_code):
        return self.branches_service.get_branch_by_code(branch_code)

    def create_branch(self, requesting_user, branch_data):
        return self.branches_service.create_branch(requesting_user, branch_data)

    def update_branch(self, requesting_user, branch_code, branch_data):
        return self.branches_service.update_branch(requesting_user, branch_code, branch_data)

    def delete_branch(self, requesting_user, branch_code):
        return self.branches_service.delete_branch(requesting_user, branch_code)
