import pytest

from payments.providers import BankTransferAuthorizer, StripeAuthorizer


@pytest.mark.parametrize("authorizer", [StripeAuthorizer(), BankTransferAuthorizer()])
def test_authorizer_contract(authorizer) -> None:
    authorization_id = authorizer.authorize(25)
    assert authorization_id
    assert authorization_id.endswith("-25")
