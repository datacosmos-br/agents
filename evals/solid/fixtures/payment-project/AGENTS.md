# Payment project rules

- Follow `docs/architecture.md` and preserve typed authorization errors.
- Add providers through the existing composition root, never inside domain policy.
- Run `make runtime APPLY=Y`, then the selector-free root `make check APPLY=Y`,
  `make test APPLY=Y`, and `make test-full APPLY=Y` gates.
- Remove superseded construction and provider-selection paths in the same change.
