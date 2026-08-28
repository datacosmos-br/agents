from dataclasses import dataclass


class InvalidOrderId(ValueError):
    """Raised when an external order identifier is empty or malformed."""


@dataclass(frozen=True)
class OrderId:
    value: str

    @classmethod
    def parse(cls, raw: str) -> "OrderId":
        value = raw.strip().upper()
        if not value.startswith("ORD-") or len(value) == 4:
            raise InvalidOrderId(raw)
        return cls(value)
