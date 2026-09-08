# Repository context

- `CheckoutService` owns order creation and requires `CheckoutRequest`.
- `PaymentGateway.charge(request, idempotency_key)` is the pinned interface.
- `OutboxPublisher` publishes only committed order events.
- Deployment runs database migration before application rollout.
- Native gates are `make check`, `make test`, and `make integration`.
- Existing authenticated checkout returns `Receipt` or the original typed
  payment/storage failure; no retry or fallback is allowed.
