# Gate evidence

- Environment: `uv run python -c "import agents_governance"`, exit 0.
- Repository check: `make check`, exit 0, zero warnings.
- Static analysis: `make static`, exit 0, zero errors.
- Tests: `make test`, exit 0, 431 passed.
- Real surface: `agentsctl check`, exit 0, current discovered catalog validated.
- Generated fixed point: `make audit`, exit 0, and its required second owner pass produced no diff.
- CI trigger contract: delivery tests exited 0 and prove `.github/workflows/**`
  selects the native workflow on both integration pushes and pull requests.
- External-token gates: `SNYK_TOKEN` and `CLIPROXY_API_KEY` are absent, so
  `make security` and `make validate-live` are `NOT EXECUTED` under the
  operator-authorized applicability rule. Neither workflow is claimed green.
