"""
REST API entry point for the Banking Domain application:
    Exposes HTTP endpoints for customer CRUD operations, backed by the
    existing Controller/Service/Repo layers. Run with:
        uvicorn app:app --reload
"""

from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from Controllers.CustomersController import CustomerController
from Day_2.BackendWithRestApi.src.main.Python.Models.Customers import Customers

app = FastAPI(title="Banking Domain REST API")
controller = CustomerController()


class CustomerCreate(BaseModel):
    customer_id: int
    name: str
    email: str


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None


def _serialize(customer: Customers) -> dict:
    return {
        "customer_id": customer.get_customer_id(),
        "name": customer.get_name(),
        "email": customer.get_email(),
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


