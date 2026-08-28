# Project contract

Keep HTTP orchestration in `src/shop/api.py`, order-list behavior in
`src/shop/orders.py`, and continuation-token policy in
`src/shop/pagination.py:PageTokenCodec`. Reuse declared dependencies; do not add a
second token codec or utility module.

The public runtime check is `python -m shop.api list-orders`. The focused native
gate is `pytest tests/test_orders.py`.
