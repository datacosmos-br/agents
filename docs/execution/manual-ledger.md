# Manual execution ledger

This is the canonical execution ledger while Gas City, Gas Town, Beads, and
Dolt are suspended. Update it after every material state change. It records
work and evidence but cannot close a phase; `DONE` still requires restoration
and closure of the canonical tracker after the approved PR is merged and
verified on `dev`.

## Active increment

- State: `IN_PROGRESS`
- Repository: `/home/marlonsc/.agents`
- Branch: `feat/agents-skill-distribution`
- Integration branch: `dev`
- Tracker/orchestration runtime: suspended; do not invoke it
- Current owner unit: connect `agentsctl audit` to the canonical inventory lock

## Operator corrections

### 2026-08-28 — manual tracking during suspension

- Prohibited prior behavior: leaving execution state only in the active session
  and Git/PR/CI while Beads, Gas Town, Gas City, and Dolt are suspended.
- Required replacement: update this manual ledger after every material state
  change without invoking or replacing the suspended runtimes.
- Authority: latest operator instruction in the active session.
- Scope: this repository for the full duration of the runtime suspension.
- Failure prevented: lost execution state and incomplete handoffs while the
  canonical tracker is unavailable.
- Closure boundary: the ledger records state but cannot satisfy canonical
  tracker closure or make a phase `DONE`.

## Published checkpoints

| Commit | Evidence |
|---|---|
| `220de69` | Preserved and pushed the inherited dirty implementation state. |
| `9bdc9e5` | Added the deterministic `agents-security` inventory/Snyk entry point and focused regressions. |

## Latest validation evidence

| Command | Exit | Decisive output |
|---|---:|---|
| `.venv/bin/agents-security --help` | 0 | `inventory` and `snyk` subcommands resolve from the installed console entry point. |
| `make security-inventory` | 0 | One tracked dependency manifest and one Snyk route. |
| `make test PYTEST_ARGS=tests/test_security.py` | 0 | 10 passed; scratch under `.test-tmp` was removed. |
| `make static` | 1 | Three Ruff findings; type gates did not run. |
| `make fmt` | 0 | Three findings fixed and 11 files formatted. |
| Manual-ledger contradiction search | 0 | No active guidance prohibits the manual execution ledger. |
| `.venv/bin/agentsctl commands audit` | 0 | Seven commands and seven eval suites validated. |
| `make static` | 1 | Ruff/format passed; Pyright reported 12 errors in `keyring.py`; Mypy did not run. |
| `make static` after typed keyring cutover | 0 | Ruff, format, Pyright, and Mypy passed with zero errors or warnings. |
| `make test` | 1 | 429 passed; only `skills.lock.json: inventory-lock-drift` failed. |
| `environment-d-loader validate` plus Bash/Zsh/Fish `env` | 0 | Storage owner materialized `/home/marlonsc/tmp` and `/home/marlonsc/.cache/cargo` consistently. |
| Focused keyring/environment/temp/CLI tests | 0 | 100 passed in managed `.test-tmp` scratch. |

## Machine-local reconciliation

The storage owner now supplies `TMPDIR`, `GOTMPDIR`, and `CARGO_HOME`. Their
three stale assignments were removed from
`~/.config/environment.d/20-xdg-storage.conf` and
`~/.config/environment.d/30-toolchains.conf`. These machine-local files are not
part of the Git commit and must remain free of storage-owned duplicates.

## Open boundary

The increment remains open. Static types, complete tests, runtime, offline and
live gates, integration merge, independent review, merge commit, post-merge
validation, and tracker closure are not yet evidenced.
