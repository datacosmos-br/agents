from shop.orders import Order, list_orders
from shop.pagination import PageTokenCodec


class TwoOrders:
    def page(self, *, limit: int) -> list[Order]:
        return [Order(id=10), Order(id=20)][:limit]


def test_list_orders_returns_token_owned_by_codec() -> None:
    codec = PageTokenCodec("test-secret")

    result = list_orders(TwoOrders(), codec, limit=2)

    assert codec.decode(str(result["next_token"])) == 20
