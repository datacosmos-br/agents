from .contracts import AuthorizationError


class StripeAuthorizer:
    def authorize(self, amount: int) -> str:
        try:
            return f"stripe-{amount}"
        except ValueError as error:
            raise AuthorizationError("stripe authorization failed") from error


class BankTransferAuthorizer:
    def authorize(self, amount: int) -> str:
        try:
            return f"bank-{amount}"
        except ValueError as error:
            raise AuthorizationError("bank authorization failed") from error
