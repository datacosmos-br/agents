from .models import Customer, Supplier


def parse_customer(raw: bytes) -> Customer:
    return Customer.model_validate_json(raw)


def parse_supplier(raw: bytes) -> Supplier:
    return Supplier.model_validate_json(raw)
