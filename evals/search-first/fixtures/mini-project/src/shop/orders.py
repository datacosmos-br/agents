from dataclasses import dataclass
from typing import Protocol

from shop.pagination import PageTokenCodec


@dataclass(frozen=True)
class Order:
    id: int


class OrderRepository(Protocol):
    def page(self, *, limit: int) -> list[Order]: ...


def list_orders(
    repository: OrderRepository,
    codec: PageTokenCodec,
    *,
    limit: int,
) -> dict[str, object]:
    orders = repository.page(limit=limit)
    next_token = str(orders[-1].id) if len(orders) == limit else None
    return {"orders": orders, "next_token": next_token}
