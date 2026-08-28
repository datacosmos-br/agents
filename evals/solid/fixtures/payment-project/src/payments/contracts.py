from typing import Protocol


class AuthorizationError(RuntimeError):
    """Authorization failed while preserving the provider cause."""


class PaymentAuthorizer(Protocol):
    def authorize(self, amount: int) -> str: ...


class ReceiptSink(Protocol):
    def publish(self, authorization_id: str) -> None: ...
