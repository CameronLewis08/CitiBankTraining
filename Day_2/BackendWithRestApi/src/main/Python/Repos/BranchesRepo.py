"""
Branch Repository for the Banking Domain REST API:
    CRUD against the 'branches' MongoDB collection.
"""

from Utilities.Database import get_database
from Models.Branches import Branches
from pymongo.errors import DuplicateKeyError


def _to_branch(doc) -> Branches:
    return Branches(doc["branch_code"], doc["location"],
                     manager_id=doc.get("manager_id"), staff_list=doc.get("staff_list", []))


class BranchesRepository:

    @staticmethod
    def get_all_branches() -> list:
        collection = get_database().branches
        return [_to_branch(doc) for doc in collection.find()]

    @staticmethod
    def get_branch_by_code(branch_code: str) -> Branches:
        if not branch_code:
            raise ValueError("Branch code must be provided.")

        collection = get_database().branches
        doc = collection.find_one({"branch_code": branch_code})
        return _to_branch(doc) if doc else None

    @staticmethod
    def create_branch(branch_data: dict) -> Branches:
        if not branch_data.get("branch_code") or not branch_data.get("location"):
            raise ValueError("Branch data must include 'branch_code' and 'location' fields.")

        branch = Branches(
            branch_data["branch_code"], branch_data["location"],
            manager_id=branch_data.get("manager_id"), staff_list=branch_data.get("staff_list"),
        )

        collection = get_database().branches
        try:
            collection.insert_one(branch.to_dict())
        except DuplicateKeyError:
            raise ValueError(f"Branch with code {branch_data['branch_code']} already exists.")

        return BranchesRepository.get_branch_by_code(branch_data["branch_code"])

    @staticmethod
    def update_branch(branch_code: str, branch_data: dict) -> Branches:
        branch = BranchesRepository.get_branch_by_code(branch_code)
        if branch is None:
            raise ValueError(f"Branch with code {branch_code} does not exist.")

        if "location" in branch_data:
            branch.location = branch_data["location"]
        if "manager_id" in branch_data:
            branch.manager_id = branch_data["manager_id"]

        collection = get_database().branches
        collection.update_one({"branch_code": branch_code}, {"$set": branch.to_dict()})

        return branch

    @staticmethod
    def delete_branch(branch_code: str) -> bool:
        if not branch_code:
            raise ValueError("Branch code must be provided for deletion.")

        collection = get_database().branches
        result = collection.delete_one({"branch_code": branch_code})
        if result.deleted_count == 0:
            raise ValueError(f"Branch with code {branch_code} does not exist.")

        return True
