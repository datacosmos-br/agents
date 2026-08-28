# Report project rules

- The approved product contract is CSV export through `reports export`.
- Follow `docs/architecture.md`; remove unsupported modes instead of hiding them.
- Preserve the raw CSV writer exception and causal chain through the CLI boundary.
- Run `python -m reports.cli export`, then project pytest, Ruff, and type gates.
