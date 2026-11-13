from datetime import datetime

from pydantic import BaseModel


class CustomerAddress(BaseModel):
    street: str
    city: str
    postal_code: str


class SupplierAddress(BaseModel):
    street: str
    city: str
    postal_code: str


class Customer(BaseModel):
    id: str
    created_at: datetime
    name: str
    email: str
    address: CustomerAddress
    credit_limit: int


class Supplier(BaseModel):
    id: str
    created_at: datetime
    name: str
    email: str
    address: SupplierAddress
    tax_id: str


class Client(BaseModel):
    id: str
    created_at: datetime
    name: str
    email: str
    address: CustomerAddress
    credit_limit: int
