from payments.checkout import CheckoutService
from payments.providers import BankTransferAuthorizer


def test_checkout_publishes_one_receipt(receipt_sink) -> None:
    service = CheckoutService(BankTransferAuthorizer(), receipt_sink)
    result = service.checkout(25)
    assert result == "bank-25"
    assert receipt_sink.published == [result]
