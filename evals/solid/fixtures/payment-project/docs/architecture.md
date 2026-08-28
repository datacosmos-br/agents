# Payment architecture

`CheckoutService` is a thin application policy. It depends on the
consumer-owned `PaymentAuthorizer` and `ReceiptSink` contracts. The composition
root chooses either `StripeAuthorizer` or `BankTransferAuthorizer` and injects it;
the service never switches on provider identity or constructs infrastructure.
