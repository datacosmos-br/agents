# Order project rules

- Follow `docs/architecture.md`; extend existing owners instead of creating a
  parallel utility or compatibility path.
- Preserve the `OrderCoordinator` public methods and typed exceptions.
- Validate runtime with `python -m orders.cli smoke`, then run `pytest` and
  `ruff check` through the project facade.
- Generated and vendor files are not editable.
