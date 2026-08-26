"""
REST API entry point for the Banking Domain application:
    Exposes HTTP endpoints for customer CRUD operations, backed by the
    existing Controller/Service/Repo layers. Run with:
        uvicorn app:app --reload
"""

from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from Controllers.CustomersController import CustomerController
from Controllers.AccountsController import AccountsController
from Models.Customers import Customers
from Models.Accounts import Accounts

app = FastAPI(title="Banking Domain REST API")
controller = CustomerController()
accounts_controller = AccountsController()


@app.exception_handler(RequestValidationError)
def handle_validation_error(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=400, content={"detail": exc.errors()})


class CustomerCreate(BaseModel):
    customer_id: int
    name: str
    email: str


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None


class AccountCreate(BaseModel):
    account_id: str
    customer_id: int
    balance: float


class AccountUpdate(BaseModel):
    customer_id: int
    balance: float


class AccountTransfer(BaseModel):
    from_account_id: str
    to_account_id: str
    amount: float


def _serialize(customer: Customers) -> dict:
    return {
        "customer_id": customer.get_customer_id(),
        "name": customer.get_name(),
        "email": customer.get_email(),
    }


def _serialize_account(account: Accounts) -> dict:
    return {
        "account_id": account.get_account_id(),
        "customer_id": account.get_customer_id(),
        "balance": account.get_balance(),
    }

@app.get("/customers")
def get_all_customers():
    customers = controller.get_all_customers()
    return [_serialize(customer) for customer in customers]

@app.get("/customers/{customer_id}")
def get_customer_by_id(customer_id: int):
    customer = controller.get_customer_by_id(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return _serialize(customer)

@app.post("/customers")
def create_customer(customer: CustomerCreate):
    try:
        new_customer = controller.create_customer(customer.model_dump())
        return _serialize(new_customer)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/customers/{customer_id}")
def update_customer(customer_id: int, customer: CustomerUpdate):
    try:
        updated_customer = controller.update_customer(customer_id, customer.model_dump(exclude_unset=True))
        return _serialize(updated_customer)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/customers/{customer_id}")
def delete_customer(customer_id: int):
    try:
        deleted = controller.delete_customer(customer_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Customer not found")
        return {"detail": "Customer deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/accounts")
def get_all_accounts():
    accounts = accounts_controller.get_all_accounts()
    return [_serialize_account(account) for account in accounts]

@app.get("/accounts/{account_id}")
def get_account_by_id(account_id: str):
    account = accounts_controller.get_account_by_id(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return _serialize_account(account)

@app.post("/accounts")
def create_account(account: AccountCreate):
    try:
        new_account = accounts_controller.create_account(account.model_dump())
        return _serialize_account(new_account)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/accounts/{account_id}")
def update_account(account_id: str, account: AccountUpdate):
    try:
        updated_account = accounts_controller.update_account(account_id, account.model_dump())
        return _serialize_account(updated_account)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/accounts/{account_id}")
def delete_account(account_id: str):
    try:
        deleted = accounts_controller.delete_account(account_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Account not found")
        return {"detail": "Account deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/accounts/transfer")
def transfer_funds(transfer: AccountTransfer):
    try:
        accounts_controller.transfer_funds(transfer.from_account_id, transfer.to_account_id, transfer.amount)
        return {"detail": "Transfer completed successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
