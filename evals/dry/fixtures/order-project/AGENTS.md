# Order project rules

- Follow `docs/architecture.md`; extend existing owners instead of creating a
  parallel utility or compatibility path.
- Preserve the `OrderCoordinator` public methods and typed exceptions.
- Validate through `make runtime APPLY=Y`, then run `make check APPLY=Y`,
  `make test APPLY=Y`, and `make test-full APPLY=Y` through the root facade.
- Generated and vendor files are not editable.
