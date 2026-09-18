# Order project rules

- Follow `docs/architecture.md`; extend existing owners instead of creating a parallel
  utility or compatibility path.
- Preserve the `OrderCoordinator` public methods and typed exceptions.
- Validate through `make runtime`, then run `make check`, `make test`, and
  `make test-full` through the root facade.
- Generated and vendor files are not editable.
