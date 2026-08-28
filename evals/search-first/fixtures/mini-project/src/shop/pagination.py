from itsdangerous import URLSafeSerializer


class PageTokenCodec:
    """Own opaque continuation-token serialization."""

    def __init__(self, secret: str) -> None:
        self._serializer = URLSafeSerializer(secret, salt="shop-pagination")

    def encode(self, order_id: int) -> str:
        return self._serializer.dumps({"order_id": order_id})

    def decode(self, token: str) -> int:
        payload = self._serializer.loads(token)
        return int(payload["order_id"])
