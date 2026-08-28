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
- Current owner unit: Plan 1 strict review of all 76 canonical skills and their
  Waza suites, starting with the `agent-wide` batch. The operator explicitly
  removed the `POLICY_BASE_SHA` prerequisite and requires manual-ledger updates
  for every material execution event.
- Concurrent out-of-scope state: Plan 2 published the central strict-policy
  baseline and has removed the repository keyring/environment-loader code,
  entrypoints, tests, and Waza consumer graph in its worktree. Existing hook
  work remains preserved and excluded from both owners' current commits.

## Operator corrections

### 2026-08-28 — Plan 1 runs without a SHA marker and records every event

- Prohibited prior behavior: blocking Plan 1 on `POLICY_BASE_SHA` or treating
  its owned-path list as permission to omit the suspended-runtime ledger.
- Required replacement: execute the six Plan 1 batches without a SHA marker,
  update this ledger after every material state change, and ask the operator
  before resolving a genuine ambiguity.
- Authority: latest explicit operator instruction in the active session.
- Scope: Plan 1 execution in the existing checkout and branch.
- Failure prevented: invented startup dependency, untracked execution, or an
  agent-selected resolution of an ambiguous contract.
- Closure boundary: ledger evidence does not make a skill, batch, or phase
  `DONE`.

### 2026-08-28 — strict plans have no named policy-baseline SHA marker

- Prohibited prior behavior: treating an operator-supplied policy-baseline SHA
  marker as a prerequisite for Plan 1 or requiring Plan 2 to publish it.
- Required replacement: Plan 1 starts independently within its declared write
  boundary, and Plan 2 creates the central policy rules without publishing a
  named baseline artifact.
- Authority: latest operator instruction in the active session.
- Scope: both strict-execution plans and active documentation that declares
  their ordering or deliverables.
- Failure prevented: blocking the 76-skill review or adding a runtime deliverable
  the operator did not request.
- Closure boundary: this correction changes plan authority only; it does not
  declare a skill, batch, or phase complete.

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
| `eaeab18` | Reconciled repository governance to this manual ledger during tracker suspension. |
| `5389b9c` | Fixed static typing and persistent managed test scratch. |
| `d849c6f` | Connected `agentsctl audit` to the catalog-owned inventory lock check/write contract. |
| `964b23e` | Replaced generic routers, removed the legacy lock, and regenerated the canonical inventory lock. |
| `7663ce0` | Normalized all 62 agent profiles to semantic capabilities and added provider-specific adapters without capability fallbacks. |
| `a4fc1fe` | Cut projection configuration and its active consumers over to the strict v4 contract. |
| `c05805e` | Reconciled active documentation and accepted ADR-0004 for the optionless fail-loud runtime. |
| `322d695` | Added the eight central strict-execution rules and removed the positive keyring rule. |

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
| `make test PYTEST_ARGS=tests/test_cli.py` | 0 | 17 passed, including canonical audit check/write/drift behavior. |
| `make audit` | 1 | Canonical `inventory-lock-drift`; write intentionally deferred until the last skill edit. |
| `make test PYTEST_ARGS=tests/test_normalize.py` (RED) | 2 | Generic-router regression failed because normalization still invented one boilerplate router. |
| `make test PYTEST_ARGS=tests/test_normalize.py` (GREEN) | 0 | 7 passed; normalization now requires an authored activation router. |
| `make audit APPLY=Y` then `make audit` | 0 | Wrote the sole `skills.lock.json` for 76 skills; unchanged check matched 76/76. |
| `make check` | 0 | 76 skills validated, exact `aihub-primary`, 131/131 token files, repository temp clean, zero normalization/description changes. |
| `make static` | 0 | Ruff, format, Pyright, and Mypy passed with zero errors or warnings. |
| `make test` | 0 | 431 passed; managed scratch was removed. |
| `make temp` | 2 | Global audit remains red: shell fallback is 6.24 GB and 45 blocking `/tmp` residues remain; foreign/unknown state was preserved. |
| Installed provider audit | 0 | Claude 2.1.246, Codex 0.149.1, Cursor 2026.07.23, Gemini 0.56.0, OpenCode 1.18.23, and Antigravity 1.1.22 resolve; Copilot is absent. |
| `make test PYTEST_ARGS=tests/test_agent_profiles.py` | 0 | 43 passed; canonical capabilities and Claude/Gemini/OpenCode adapters are covered. |
| `make static` after agent capability cutover | 0 | Ruff, format, Pyright, and Mypy passed with zero errors or warnings. |
| `.venv/bin/agentsctl validate` | 0 | 76 skills and the strict agent-profile schema validated. |
| Focused projection v4 tests | 0 | 73 passed across projection, CLI, and strict 56-cell configuration coverage. |
| Projection v3 residue search | 0 | No v3 target keys, dual-read helpers, manifest-v2 wording, or Copilot-to-Claude adapter identity remain under `src`, `tests`, or `config`. |
| `make static` after projection v4 consumer cutover | 0 | Ruff, format, Pyright, and Mypy passed with zero errors or warnings across 45 source files. |
| Plan-first boundary inspection | 0 | Clean worktree at `a4fc1fe`; the first mutation created only the two standalone strict-execution plans. |
| Strict-plan startup-prerequisite residue search | 0 | Both active Plan 1 surfaces contained no removed startup prerequisite. |
| `rg -n --hidden --glob '!.git/**' 'POLICY_BASE[_]SHA' .` | 1 | No output; ripgrep's no-match status proves the literal identifier is absent from the checkout outside `.git`. |
| `git diff --check` after Plan 2 documentation reconciliation | 0 | Root instructions, README, master v7, ADRs, and security evidence contain no whitespace defects. |
| Legacy CLI contradiction search outside historical ledger | 0 | No active documentation contains nested `agentsctl` runtime commands, CLI options, `APPLY=Y`, `PROJECT_ROOTS`, or `SCOPE` selectors. |
| `make help` diagnostic before Make cutover | 0 | The current Make surface still advertises legacy option-bearing runtime routes; Make/CLI implementation remains intentionally red for the later Plan 2 owner unit. |
| `make test PYTEST_ARGS='tests/test_rules.py tests/test_rule_adapters.py tests/test_delivery_contracts.py'` | 0 | 59 rule discovery, provider rendering, and delivery-contract tests passed after the eight strict central policies were added and the keyring rule removed. |
| `git diff --check` after central strict-policy cutover | 0 | No whitespace defects in the policy unit. |
| `make test PYTEST_ARGS=tests/test_required_environment.py` (RED) | 2 | Collection failed because the strict process-environment owner did not yet exist. |
| `make test PYTEST_ARGS='tests/test_required_environment.py tests/test_waza_environment.py tests/test_waza_config.py'` (GREEN) | 0 | 27 direct-environment and Waza-owner tests passed after removing loaders and keyring consumers. |
| `make static` after repository keyring extermination | 0 | Ruff, format, Pyright, and Mypy passed with zero errors or warnings across 44 source files. |
| Repository keyring/runtime-loader residue gate | 0 | Removed console binaries are absent and no keyring, secret-tool, environment-loader, or Waza-keyring reference remains in active source, tests, config, Make, workflows, commands, agents, or tracked hooks. |
| `make test PYTEST_ARGS=tests/test_catalog.py` (RED) | 1 | Five failures proved the catalog rejected the new strict-policy namespace. |
| `make test PYTEST_ARGS=tests/test_catalog.py` (GREEN) | 0 | 27 catalog tests passed; only the nine declared strict policy tags are accepted, without requiring incomplete parallel skill batches. |
| `rg` semantic pre-edit scan for `agent-introspection-debugging` | 0 | The first reviewed bundle still authorizes retry/backoff/transient-recovery language, a `partial` result, and references three absent skill owners; correction is required in the canonical bundle/eval. |

## Machine-local reconciliation

The storage owner now supplies `TMPDIR`, `GOTMPDIR`, and `CARGO_HOME`. Their
three stale assignments were removed from
`~/.config/environment.d/20-xdg-storage.conf` and
`~/.config/environment.d/30-toolchains.conf`. These machine-local files are not
part of the Git commit and must remain free of storage-owned duplicates.

The ignored repository-local directory literally named `$HOME` contained only
Fish/Mise cache/state from an earlier unexpanded environment. After confirming
no open process, database, special file, or tracked content, it was moved to the
same-filesystem user trash with `gio trash`. It remains recoverable there and
the repository-scoped temp audit now passes.

## Open boundary

The increment remains open. Runtime strict extermination beyond the removed
keyring/loader graph, projection v4 activation semantics, agent/rule evals,
offline/live Waza,
the complete native gate matrix, resolution of the global temp findings,
integration merge, independent review, merge commit, post-merge validation, and
tracker closure are not yet evidenced.
