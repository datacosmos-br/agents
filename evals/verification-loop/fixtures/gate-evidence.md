# Gate evidence

- Environment: `uv run python -c "import agents_governance"`, exit 0.
- Repository check: `make check`, exit 0, zero warnings.
- Static analysis: `make static`, exit 0, zero errors.
- Tests: `make test`, exit 0, 431 passed.
- Real surface: `agentsctl check`, exit 0, `PASS: 76 skills validated`.
- Generated fixed point: `make audit`, exit 0, and its required second owner pass produced no diff.
