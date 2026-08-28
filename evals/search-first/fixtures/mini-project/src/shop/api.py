from shop.orders import Order, list_orders
from shop.pagination import PageTokenCodec


class MemoryOrders:
    def page(self, *, limit: int) -> list[Order]:
        return [Order(id=value) for value in range(1, limit + 1)]


def main() -> None:
    result = list_orders(MemoryOrders(), PageTokenCodec("runtime-secret"), limit=2)
    print(result["next_token"])


if __name__ == "__main__":
    main()
