from .providers import BankTransferAuthorizer, StripeAuthorizer


class CheckoutService:
    def __init__(self, receipt_sink) -> None:
        self.receipt_sink = receipt_sink

    def checkout(self, provider: str, amount: int) -> str:
        if provider == "stripe":
            authorization_id = StripeAuthorizer().authorize(amount)
        elif provider == "bank":
            authorization_id = BankTransferAuthorizer().authorize(amount)
        else:
            raise ValueError(f"unknown provider: {provider}")
        self.receipt_sink.publish(authorization_id)
        return authorization_id
