"""
REST API entry point for the Banking Domain application:
    Exposes HTTP endpoints for user (role-based), branch, and account
    operations, backed by the Controller/Service/Repo layers. Run with:
        uvicorn app:app --reload
"""

from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from Controllers.UsersController import UsersController
from Controllers.BranchesController import BranchesController
from Controllers.AccountsController import AccountsController
from Models.Users import Users
from Models.Branches import Branches
from Models.Accounts import Accounts
from Utilities.Status import AccountStatus

app = FastAPI(title="Banking Domain REST API")
users_controller = UsersController()
branches_controller = BranchesController()
accounts_controller = AccountsController()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
def handle_validation_error(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=400, content={"detail": exc.errors()})


@app.exception_handler(PermissionError)
def handle_permission_error(request: Request, exc: PermissionError):
    return JSONResponse(status_code=403, content={"detail": str(exc)})


def _require_user(user_id: int) -> Users:
    user = users_controller.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="Unknown requesting_user_id.")
    return user


class UserCreate(BaseModel):
    name: str
    email: str
    user_id: Optional[int] = None
    role: Optional[str] = None
    branch_code: Optional[str] = None
    password: Optional[str] = None
    requesting_user_id: Optional[int] = None


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    branch_code: Optional[str] = None
    requesting_user_id: int


class LoginRequest(BaseModel):
    email: str
    password: str


class BranchCreate(BaseModel):
    branch_code: str
    location: str
    manager_id: Optional[int] = None
    requesting_user_id: int


class BranchUpdate(BaseModel):
    location: Optional[str] = None
    manager_id: Optional[int] = None
    requesting_user_id: int


class AccountCreate(BaseModel):
    account_id: Optional[str] = None
    owner_id: Optional[int] = None
    balance: float
    branch_code: str
    account_type: str
    requesting_user_id: int


class AmountRequest(BaseModel):
    amount: float
    requesting_user_id: int


class AccountTransfer(BaseModel):
    requesting_user_id: int
    from_account_id: str
    to_account_id: str
    amount: float


def _serialize_user(user: Users) -> dict:
    return {
        "user_id": user.get_user_id(),
        "name": user.get_name(),
        "email": user.get_email(),
        "role": user.get_role().value,
        "branch_code": user.get_branch_code(),
    }


def _serialize_branch(branch: Branches) -> dict:
    return {
        "branch_code": branch.get_branch_code(),
        "location": branch.get_location(),
        "manager_id": branch.manager_id,
        "staff_list": branch.staff_list,
    }


def _serialize_account(account: Accounts, owner_name: Optional[str] = None) -> dict:
    return {
        "account_id": account.get_account_id(),
        "owner_id": account.get_owner_id(),
        "owner_name": owner_name,
        "balance": account.get_balance(),
        "branch_code": account.get_branch_code(),
        "account_type": account.get_account_type().value,
        "status": account.get_status().value,
    }


@app.post("/login")
def login(payload: LoginRequest):
    try:
        user = users_controller.login(payload.email, payload.password)
        return _serialize_user(user)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@app.get("/users")
def get_all_users(
    requesting_user_id: int, skip: int = 0, limit: Optional[int] = None, search: Optional[str] = None,
):
    requesting_user = _require_user(requesting_user_id)
    # Fetch one extra row beyond what's requested so the caller can tell
    # whether another page exists (a full page back = more to load) without
    # a separate count query or changing the response from a plain array.
    fetch_limit = limit + 1 if limit is not None else None
    users = users_controller.get_all_users(requesting_user, skip=skip, limit=fetch_limit, search=search)
    if limit is not None:
        users = users[:limit]
    return [_serialize_user(user) for user in users]


@app.get("/users/{user_id}")
def get_user_by_id(user_id: int, requesting_user_id: int):
    requesting_user = _require_user(requesting_user_id)
    user = users_controller.view_user_profile(requesting_user, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return _serialize_user(user)


@app.post("/users")
def create_user(payload: UserCreate):
    # requesting_user_id is optional here: omitting it is the public
    # self-signup path (see UsersService.create_user), not an auth gap.
    requesting_user = _require_user(payload.requesting_user_id) if payload.requesting_user_id is not None else None
    try:
        data = payload.model_dump(exclude={"requesting_user_id"}, exclude_none=True)
        new_user = users_controller.create_user(requesting_user, data)
        return _serialize_user(new_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/users/{user_id}")
def update_user(user_id: int, payload: UserUpdate):
    requesting_user = _require_user(payload.requesting_user_id)
    try:
        data = payload.model_dump(exclude={"requesting_user_id"}, exclude_unset=True)
        updated_user = users_controller.update_user(requesting_user, user_id, data)
        return _serialize_user(updated_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/users/{user_id}")
def delete_user(user_id: int, requesting_user_id: int):
    requesting_user = _require_user(requesting_user_id)
    try:
        users_controller.delete_user(requesting_user, user_id)
        return {"detail": "User deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/branches")
def get_all_branches(
    requesting_user_id: int, skip: int = 0, limit: Optional[int] = None, search: Optional[str] = None,
):
    requesting_user = _require_user(requesting_user_id)
    fetch_limit = limit + 1 if limit is not None else None
    branches = branches_controller.get_all_branches(requesting_user, skip=skip, limit=fetch_limit, search=search)
    if limit is not None:
        branches = branches[:limit]
    return [_serialize_branch(branch) for branch in branches]


@app.post("/branches")
def create_branch(payload: BranchCreate):
    requesting_user = _require_user(payload.requesting_user_id)
    try:
        data = payload.model_dump(exclude={"requesting_user_id"})
        new_branch = branches_controller.create_branch(requesting_user, data)
        return _serialize_branch(new_branch)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/branches/{branch_code}")
def update_branch(branch_code: str, payload: BranchUpdate):
    requesting_user = _require_user(payload.requesting_user_id)
    try:
        data = payload.model_dump(exclude={"requesting_user_id"}, exclude_unset=True)
        updated_branch = branches_controller.update_branch(requesting_user, branch_code, data)
        return _serialize_branch(updated_branch)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/branches/{branch_code}")
def delete_branch(branch_code: str, requesting_user_id: int):
    requesting_user = _require_user(requesting_user_id)
    try:
        branches_controller.delete_branch(requesting_user, branch_code)
        return {"detail": "Branch deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/accounts")
def get_all_accounts(
    requesting_user_id: int, owner_id: Optional[int] = None,
    skip: int = 0, limit: Optional[int] = None, search: Optional[str] = None,
):
    requesting_user = _require_user(requesting_user_id)
    try:
        fetch_limit = limit + 1 if limit is not None else None
        accounts = accounts_controller.get_all_accounts(
            requesting_user, owner_id, skip=skip, limit=fetch_limit, search=search)
        if limit is not None:
            accounts = accounts[:limit]
        # One batch lookup for the whole page's owner names, rather than a
        # $lookup join per request or an N+1 fetch per account - the join
        # cost stays flat as the total accounts/users collections grow,
        # since it's bounded by page size, not table size.
        owner_ids = {account.get_owner_id() for account in accounts}
        owners_by_id = {
            owner.get_user_id(): owner.get_name()
            for owner in users_controller.get_users_by_ids(list(owner_ids))
        }
        return [
            _serialize_account(account, owners_by_id.get(account.get_owner_id()))
            for account in accounts
        ]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/accounts/{account_id}")
def get_account_by_id(account_id: str, requesting_user_id: int):
    requesting_user = _require_user(requesting_user_id)
    account = accounts_controller.get_account_by_id(requesting_user, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return _serialize_account(account)


@app.post("/accounts")
def create_account(payload: AccountCreate):
    requesting_user = _require_user(payload.requesting_user_id)
    try:
        data = payload.model_dump(exclude={"requesting_user_id"}, exclude_none=True)
        new_account = accounts_controller.create_account(requesting_user, data)
        return _serialize_account(new_account)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/accounts/{account_id}/deposit")
def deposit(account_id: str, payload: AmountRequest):
    requesting_user = _require_user(payload.requesting_user_id)
    try:
        account, result = accounts_controller.deposit(requesting_user, account_id, payload.amount)
        return {"account": _serialize_account(account), "result": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/accounts/{account_id}/withdraw")
def withdraw(account_id: str, payload: AmountRequest):
    requesting_user = _require_user(payload.requesting_user_id)
    try:
        account, result = accounts_controller.withdraw(requesting_user, account_id, payload.amount)
        return {"account": _serialize_account(account), "result": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/accounts/{account_id}/transactions")
def get_transactions(account_id: str, requesting_user_id: int):
    requesting_user = _require_user(requesting_user_id)
    account = accounts_controller.get_account_by_id(requesting_user, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account.get_transaction_history()


@app.post("/accounts/{account_id}/deactivate")
def deactivate_account(account_id: str, requesting_user_id: int):
    requesting_user = _require_user(requesting_user_id)
    try:
        account = accounts_controller.set_status(requesting_user, account_id, AccountStatus.INACTIVE)
        return _serialize_account(account)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/accounts/{account_id}/reactivate")
def reactivate_account(account_id: str, requesting_user_id: int):
    requesting_user = _require_user(requesting_user_id)
    try:
        account = accounts_controller.set_status(requesting_user, account_id, AccountStatus.ACTIVE)
        return _serialize_account(account)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/accounts/{account_id}")
def delete_account(account_id: str, requesting_user_id: int):
    requesting_user = _require_user(requesting_user_id)
    try:
        deleted = accounts_controller.delete_account(requesting_user, account_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Account not found")
        return {"detail": "Account deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/branches/{branch_code}/accounts")
def search_accounts_by_branch(
    branch_code: str, requesting_user_id: int,
    account_type: Optional[str] = None, status: Optional[str] = None,
):
    requesting_user = _require_user(requesting_user_id)
    try:
        accounts = accounts_controller.search_accounts_by_branch(requesting_user, branch_code, account_type, status)
        return [_serialize_account(account) for account in accounts]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/branches/{branch_code}/users")
def search_users_by_branch(
    branch_code: str, requesting_user_id: int,
    role: Optional[str] = None, name: Optional[str] = None,
):
    requesting_user = _require_user(requesting_user_id)
    try:
        users = users_controller.search_users_by_branch(requesting_user, branch_code, role, name)
        return [_serialize_user(user) for user in users]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/accounts/transfer")
def transfer_funds(payload: AccountTransfer):
    requesting_user = _require_user(payload.requesting_user_id)
    try:
        result = accounts_controller.transfer_funds(
            requesting_user, payload.from_account_id, payload.to_account_id, payload.amount
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
