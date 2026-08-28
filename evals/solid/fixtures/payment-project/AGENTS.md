# Payment project rules

- Follow `docs/architecture.md` and preserve typed authorization errors.
- Add providers through the existing composition root, never inside domain policy.
- Run `python -m payments.cli smoke`, then the project `pytest`, Ruff, and type gates.
- Remove superseded construction and provider-selection paths in the same change.
