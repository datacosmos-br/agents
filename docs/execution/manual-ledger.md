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

### 2026-08-28 — Plan 1 accepts CLI cutovers and keeps editing skills

- Prohibited prior behavior: stopping semantic skill review because a concurrent
  CLI/Make cutover removed a formerly focused command, or invoking a private CLI
  route to recreate that gate.
- Required replacement: Plan 1 edits only canonical skill bundles and their
  evals, never calls `agentsctl` directly, accepts the current optionless CLI,
  and uses the Make targets advertised by `make help` at the batch boundary.
- Authority: latest explicit operator instruction and approved revised plan.
- Scope: all six Plan 1 batches in this checkout.
- Failure prevented: cross-boundary runtime work, restoration of legacy CLI
  grammar, or abandonment of the 74 unreviewed skills.
- Closure boundary: a batch still requires green canonical Make gates before
  its WIP commit and push.

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
| `2156471` | Exterminated repository keyring/loaders and established required process-environment ownership. |
| `ffc59d6` | Restricted catalog policy tags to the nine declared strict-execution policies. |
| `a0fe936` | Replaced the legacy/nested CLIs with the sole eight-verb optionless `agentsctl` facade. |
| `3cf24a1` | Removed legacy Make/Waza routes and restricted Make runtime calls to public optionless verbs. |
| `b93f66d` | Added whole-source strict AST enforcement and cut environment, projection config, security, and token owners over to immediate exceptions. |
| `e178d97` | Replaced aggregate catalog findings with first-defect discovery and strict inventory-lock exceptions. |
| `c8ea26a` | Replaced agent/rule aggregate findings and neutral unsupported results with first-defect exceptions; 51 focused tests, Pyright, Mypy, Ruff, and the 62-agent/40-rule canonical inventories passed before the WIP push. |
| `75a627c` | Collapsed metadata and governance validation into first-defect owners, deleted the redundant normalization protocol/tests, and removed 1,370 net lines; 31 focused tests and focused static analysis passed. `origin/dev` remained 0 commits ahead after fetch, so no merge was required. |

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
| Plan 1 central-tag owner recheck | 0 | The catalog now accepts exactly the nine declared `policy:*` tags; Plan 1 can proceed without a `POLICY_BASE_SHA`, and concurrent runtime/test changes remain excluded from its batch commits. |
| Plan 1 `agent-introspection-debugging` owner edit | — | Added directly applicable strict policy tags, removed retry/fallback and absent-owner guidance, required one preflighted correction, and strengthened all three Waza roles. |
| `make check SKILL=agent-introspection-debugging` (sandbox attempt) | 2 | `uv` could not create its configured cache temporary file on the read-only sandbox filesystem; no skill gate executed. |
| `make check SKILL=agent-introspection-debugging` (approved run, interrupted observation) | not captured | Validation, exact Waza model, token budget, and repository-temp stages printed PASS; the turn interruption detached observation while `agentsctl normalize` was still running, so no final exit code is claimed. |
| `make check SKILL=agent-introspection-debugging` | 0 | All 76 sources validated; `aihub-primary` had zero drift; the edited router measured 1,173/5,000 BPE tokens; repository temp, normalization, and descriptions were clean. |
| `make spec SKILL=agent-introspection-debugging` (RED) | 2 | Coverage was 0/1 because no task exercised the description vocabulary `agent behavior, session recovery, tool debugging`; the eval owner must expose those activation facets. |
| `make spec SKILL=agent-introspection-debugging` (GREEN) | 0 | Coverage is 1/1; the material happy-path task now covers agent behavior, session recovery, and tool debugging, and managed scratch was removed. |
| Plan 1 `anti-phase-skip` owner edit | — | Added the directly exercised atomic, causal, fail-loud, no-fallback, preflight, and zero-residue tags; removed warning-as-blocker wording and made the fail-closed eval require the first missing prerequisite with zero transition effects. |
| `make check SKILL=anti-phase-skip` (RED) | 2 | `Makefile:67` invoked the removed legacy `agentsctl validate --skill` route; the strict CLI raised `ValueError: agentsctl requires exactly one optionless verb` before any skill gate. Make/CLI are outside Plan 1 scope, so no bypass or retry was attempted. |
| `.venv/bin/agentsctl help` after single-verb cutover | 0 | Printed exactly `help`, `doctor`, `check`, `sync`, `evaluate`, `secure`, `clean`, and `live`; no nested command or option is accepted. |
| `make static` after single-CLI cutover | 0 | Ruff, format, Pyright, and Mypy passed with zero errors or warnings across 45 source files. |
| `make test PYTEST_ARGS='tests/test_cli.py tests/test_security.py tests/test_agent_profiles.py tests/test_commands.py tests/test_required_environment.py'` | 0 | 108 focused tests passed; the old CLI surface and the parallel `agents-security` entry point/tests are absent. |
| `git diff --check` after single-CLI cutover | 0 | No whitespace defects in the Plan 2 CLI/runtime/security unit or preserved concurrent work. |
| `make help` after Make cutover | 0 | Exposed the required docs, audit, check, static, shell, build, test, spec, coverage, providers, projection, ci, security, temp, and validate-live development gates without selectors. |
| `make docs` after Make cutover | 0 | Four delivery-contract tests passed, including the regression that permits only optionless public runtime verbs in Make. |
| `make static` after Make cutover | 0 | Ruff, format, Pyright, and Mypy passed with zero errors or warnings across 45 source files. |
| Active Make/config/CLI residue search | 1 | No option-bearing `agentsctl`, removed nested verb, `agents-security`, `config/waza.mk`, or Waza shell-wrapper invocation remains in Make, config, source, packaging, or workflows. |
| `make test PYTEST_ARGS=tests/test_strict_execution.py` (RED) | 2 | The new whole-source AST gate exposed 125 non-cleanup catches, five normalized child processes, and 33 finding/default protocol owners before the first strict owner batch. |
| Focused strict environment/projection-config/security tests | 0 | 27 tests passed after direct environment indexing, raw JSON errors, immediate security validation, and native child-process propagation. |
| `make static` after first strict owner batch | 0 | Ruff, format, Pyright, and Mypy passed with zero errors or warnings across 46 source files. |
| Whole-source strict inventory after first owner batch | 0 | Remaining red inventory is explicit: 119 forbidden catches, two `check=False`, 24 finding-protocol declarations, and three `os.environ.get` defaults. |
| Strict catalog source audit | 0 | `catalog.py` contains zero exception catches and zero finding declarations; discovery, tags, physical identity, and inventory lock raise on the first defect. |
| `make test PYTEST_ARGS="tests/test_catalog.py -k 'not canonical_catalog_is_exhaustive_disjoint_and_agents_owned'"` | 0 | 26 catalog tests passed; the one real-lock assertion stayed excluded only because concurrent Plan 1 skill edits deliberately keep that gate red until handoff. |
| `make static` after strict catalog cutover | 0 | Ruff, format, Pyright, and Mypy passed with zero errors or warnings across 46 source files. |
| Strict command owner audit | 0 | `commands.py` and `command_evals.py` contain zero catches and zero finding declarations; source, suite, rendering, budget, and support defects raise immediately. |
| `make test PYTEST_ARGS='tests/test_commands.py tests/test_command_evals.py'` | 0 | 28 strict command and seven-family eval tests passed. |
| Copilot command identity residue audit | 0 | All seven command suites classify Copilot under unsupported providers; no command renderer reuses Claude output for Copilot. |
| `make static` after strict command cutover | 0 | Ruff, format, Pyright, and Mypy passed with zero errors or warnings across 46 source files. |
| Plan 1 critical completeness audit | 0 | Only 2/76 skills had `policy:strict-execution`: `agent-wide` 2/26, `project-wide` 0/22, `technology` 0/8, `framework` 0/3, `tool` 0/16, and `domain` 0/1; all 76 eval suites expose the three required task files. |
| `make help` after optionless CLI cutover | 0 | The canonical development surface now exposes global `check` and `spec`; Plan 1 will not call `agentsctl` directly or recreate removed focused CLI syntax. |
| Plan 1 repair of the first two `agent-wide` slugs | — | `agent-introspection-debugging` now references atomic effects and forbids preventive follow-up before current resolution; `anti-phase-skip` fail-closed now requires the first missing prerequisite, zero transition effects, and manual-ledger tracking during suspension. |
| Plan 1 review: `article-writing`, `brand-voice`, `caveman` | — | Added justified strict/fail-loud/no-fallback/preflight tags; made missing sources stop article/profile publication, made durable voice persistence atomic, removed an absent downstream owner and stale-profile reuse, and made evidence-free status claims fail without publication. |
| Plan 1 review: `content-engine`, `context-canary`, `crosspost` | — | Made complete source/destination/voice preflight mandatory, removed generic or reduced campaign fallback, replaced warning-and-resume canary behavior with atomic checkpoint-and-stop, and removed default sequencing while requiring complete validated cross-platform publication. |
| Plan 1 review: `deep-research`, `dispatch-agent`, `frontend-slides` | — | Removed private provider config, arbitrary research quotas, provider switching, provider-specific subagent instructions, general-agent preference, Gas City coupling, remote font dependency, deferred preview cleanup, automatic opener use, and manual conversion fallback; added complete preflight, causal/atomic dispatch, and zero-effect fail-closed evals. |
| Plan 1 review: `governance-audit`, `human-writing-style`, `investor-materials` | — | Replaced suspended Beads command recipes with provider-independent static audit contracts, made causal governance defects blocking, removed private authority paths and three nonexistent writing references, and required fact-complete atomic investor asset publication with zero output on conflicts. |
| Plan 1 review: `investor-outreach`, `make-check`, `market-research` | — | Removed generic voice and fixed cadence fallback, required complete sourced outbound preflight, made missing Make targets stop without raw-tool substitution or unauthorized owner edits, and required decision/source/tool preflight with no alternate market report or estimate. |
| Plan 1 pre-edit audit: `operator-correction-learning`, `prompt-safety-review`, `safe-delete` | — | The correction workflow lacked explicit strict-policy ownership for its atomic cutover; prompt safety duplicated a generic provider-oriented manual and prescribed alternative patterns instead of a compact fail-closed review contract; safe deletion had strong behavior but lacked central policy references and explicit zero-effect Waza assertions. |
| Plan 1 review: `operator-correction-learning`, `prompt-safety-review`, `safe-delete` | — | Added ordered strict-policy references; made correction reconciliation a preflighted atomic cutover with causal gates and zero semantic residue; replaced the 250-line generic prompt manual with a compact evidence-based, no-keyring, no-fallback governed-review contract; and made deletion propagate cleanup failures without retry, substitution, partial targets, or broad effects. All three Waza suites now assert material success, zero-effect fail-closed behavior, and no activation fallback. |
| Plan 1 pre-edit audit: final six `agent-wide` bundles | — | `skill-governance`, `strategic-compact`, and `summarization` need explicit strict ownership and stronger zero-effect eval assertions; `sprint-closure` and `verification-loop` embed stale option-bearing CLI and private owner names; `video-editing` embeds a fixed multi-provider/model pipeline, alternate services, manual finalization, and partial intermediate effects. |
| Plan 1 review: final six `agent-wide` bundles | — | Added strict owners and material/zero-effect/non-trigger assertions to skill governance, compaction, and summarization; rewrote closure and verification around current owner-discovered commands and optionless `agentsctl check`, first-causal-failure propagation, atomic closure, and zero residue; replaced the fixed video provider/model ladder with one fully preflighted selected toolchain, immutable sources, causal subprocesses, verified atomic publication, environment-only credentials, and zero intermediate residue. |
| Plan 1 `agent-wide` residue audit | 0 | All 26 routers carry `policy:strict-execution`; no active option-bearing or removed `agentsctl` command remains. Two non-failure phrases containing `skip`/`catch` were still ambiguous, so they were replaced with explicit no-preview and detection wording before gates. Prohibitive mentions of `/tmp`, keyring, fallback, retries, warnings, skips, partial effects, profiles, and aliases remain only where the strict contract rejects them or fixtures exercise them. |
| `make check` after the complete `agent-wide` review (RED) | 2 | The optionless Make owner invoked `agentsctl check` and stopped before skill validation with `ValueError: canonical skill inventory lock differs from discovery: /home/marlonsc/.agents/skills.lock.json`. Plan 1 prohibits regenerating or editing `skills.lock.json`; no later gate, commit, push, or next-batch edit was attempted. |
| Operator authorization to regenerate `skills.lock.json` | — | The operator explicitly designated this lane as owner of the generated lock. Current `make audit` is read-only and no mutating lock command exists; regeneration will therefore compose the canonical `Catalog.render_inventory()` owner with the canonical destination-local `atomic_write_text()` publication primitive, without editing runtime or CLI. |
| Canonical `skills.lock.json` regeneration | 0 | `Catalog.render_inventory()` was published with `atomic_write_text()`; resulting SHA-256 is `2124f5e36735491f02957f8479f6380f37dcf25c551fe4a8f439dffe49e0f365`. No runtime, CLI, schema, or Make source was edited. |
| Canonical inventory fixed point | 0 | A second owner generation produced the identical SHA-256 `2124f5e36735491f02957f8479f6380f37dcf25c551fe4a8f439dffe49e0f365`; the lock converged without a second-byte change. |

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
