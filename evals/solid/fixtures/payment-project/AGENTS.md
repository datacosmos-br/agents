# Payment project rules

- Follow `docs/architecture.md` and preserve typed authorization errors.
- Add providers through the existing composition root, never inside domain policy.
- Run `make runtime`, then the selector-free root `make check`, `make test`, and
  `make test-full` gates.
- Remove superseded construction and provider-selection paths in the same change.
