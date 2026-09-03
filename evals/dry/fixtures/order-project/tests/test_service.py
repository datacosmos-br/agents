import pytest
from orders.identity import InvalidOrderId
from orders.service import OrderCoordinator


def test_invalid_identifier_preserves_typed_public_error(repository, audit) -> None:
    with pytest.raises(InvalidOrderId):
        OrderCoordinator(repository, audit).create_order(" ", 10)


def test_cancel_is_idempotent(repository_with_cancelled_order, audit) -> None:
    service = OrderCoordinator(repository_with_cancelled_order, audit)
    service.cancel_order(" ord-1 ")
    assert repository_with_cancelled_order.cancel_calls == 0
    assert audit.events == []


def test_csv_contract(repository, audit) -> None:
    repository.rows_result = [("ORD-1", "open", 10)]
    assert OrderCoordinator(repository, audit).export_csv() == (
        "id,status,total\nORD-1,open,10\n"
    )
