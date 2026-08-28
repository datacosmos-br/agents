# Gate evidence

- Environment: `uv run python -c "import agents_governance"`, exit 0.
- Lint and format: `make check CHECK_GATES=lint,format`, exit 0, zero warnings.
- Types: `make check CHECK_GATES=pyrefly,mypy,pyright`, exit 0, zero errors.
- Tests: `make test FILE=tests/test_projection.py`, exit 0, 31 passed.
- Real surface: `agentsctl projections --scope projects --project-root fixture --check`, exit 0, `PASS: projections converged`.
- Generated fixed point: second apply produced no diff.
