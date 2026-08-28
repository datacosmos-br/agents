# Report project rules

- The approved product contract is CSV export through `reports export`.
- Follow `docs/architecture.md`; remove unsupported modes instead of hiding them.
- Preserve `ExportError` and its cause at the CLI boundary.
- Run `python -m reports.cli export`, then project pytest, Ruff, and type gates.
