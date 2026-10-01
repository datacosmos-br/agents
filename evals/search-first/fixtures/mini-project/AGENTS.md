# Project contract

Keep HTTP orchestration in `src/shop/api.py`, order-list behavior in
`src/shop/orders.py`, and continuation-token policy in
`src/shop/pagination.py:PageTokenCodec`. Reuse declared dependencies; do not add a
second token codec or utility module.

The public runtime check is `make runtime`. The affected native gate is `make test`,
which runs with the shared testmon cache; the full gate is `make test-full`, run locally
without testmon.
