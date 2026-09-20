# Stabilization record — multi-repo round 2026-09-20 (agents-dedicated)

Cross-repo stabilization round executed under the coordinator routing
(DECISOES 2/3, flext/claude): agents-dedicated owns the agents repo,
queue (a) of algar-oud-mig, mirror-sync of the flext mirrors, and
read-only verification of the flext-sh landings. Everything below is
evidence-backed in beads (agents/algar/flext stores).

## algar-oud-mig (`0.12.0-dev` integration)

- Measured: 17/20 gates green (peer had cleared 15 classes); red was
  mypy 198, pyrefly 53, codemod 24.
- mypy 198 → 0: one root pattern — `r`/`t` read as `Any` through the
  lazy facades (`scripts`, `tests`, `algar_oud_mig`) in scripts/tests/
  examples. Cutover to the owners: `r` → `flext_core`, `t` → the
  `algar_oud_mig` root typings, `tf` → `flext_tests`, `s` →
  `examples.base`. Collection restored (243 tests, 0 errors) and the
  19 `no-any-return` findings gone.
- pyrefly 53 → 0: same cutover law (services half by the concurrent
  session commit `2d3d4348`, examples/scripts half this round).
- codemod 24: BLOCKED — the mod runner assembles its temp root without
  `__snapshots__/`, so any new rule with invalid cases fails validation
  before apply. Flext-infra owner lane (family of `flext-6ep5y`).
- Lane: `wip/stabilize-0.12-algar-20260919` (pushed; commits
  `b0cca9c6`→`7ed2f015` + this doc's branch). Merge per coordinator
  decision.

## ai-hub (`dev` integration)

- `origin/dev` standalone crash FIXED: the lost constants block
  (`GOVERNANCE_COMMENT_CLOSE`, `OWNER_FILE_MODE`, `WHEEL_GLOB`,
  `RECORD_SUFFIX`, `PYTHON_MODULE_ARGV_PREFIX`) restored via PR #815
  (merged). Adopted fleet fixes: `agents-governance` over https
  (escort of the closed #810) and the #814 law "unavailable credential =
  NOT EXECUTED, not a violation".
- Remaining red was the flext-infra transaction layer (lazy-init phase
  dir with no authorized files) — fixed upstream in flext-infra
  (#777/#780 + `caeddadae` mise-artifacts noop for `flext-6ep5y`) and
  adopted by ai-hub's branch pin.
- Runtime evidence chain for the AH v2 series (`ag-lw57.10`, `ag-bwqu`,
  `ag-lw57.4`, `ag-lw57.7`, `ag-vblj.5`) queued on the sane tip.

## flext workspace (stabilize worktree `wip/stabilize-0.12-root-20260919`)

- Bootstrap debt closed: 14 members lacked their own venvs (the cause
  of the uniform `exit=2` in the workspace fix) — individual setup done;
  fix 32/32, fmt 32/32.
- Import cycle of the convergence fixed at the owner
  (`_models/_defaults`, not the facade) + the `ConformMisc`→
  `ConformFilePlans` rename completed; committed `020728af4` (branch
  `wip/stabilize-0.12-flext-infra-20260919`), gitlink rolled
  (`5082ca87ea`).
- Remaining grind mapped per member (namespace 333, pyrefly 151,
  codemod 35, duplication 16, types ~43) = the `ag-q4w1` campaign,
  executed after the flext landing (hold respected).
- Layout-gate defect diagnosed for the round-2 executor: the engine
  passes (warning severity, 0 actionable) while the stage fails with
  0 findings — wrapper path, not engine.

## flext-cli (flext-sh source of truth)

- PR flext-sh/flext-cli#176 MERGED (`45a706fd`): `AtomicFileState.
  link_count` observed (not constrained) — completes `d75f50d5`; the
  pydantic crash on uv-hardlinked destinations was the fleet-wide
  `gen fixed point` blocker. Physical-tree inventory cleanup refusal
  preserved as a causal typed failure. Companion: canonical gen render
  committed on the PR branch.

## Coordination

- Channels: `[coord]` grammar per DECISOES 2/3; every milestone mailed
  with `--notify`; mirror-sync duty armed (flext-sh → datacosmos-br ff,
  `[coord] mirror` announcements, `[coord] blocker` on divergence).
- Ownership taken even on claimed/in_progress beads: `ag-q4w1`,
  `ag-a11`, `ag-m9lu`, `ag-zrh(.4)`, `ag-vmn` (tracking), `algar-66y`,
  `algar-wiq`, `flext-6ep5y` (closed with fix evidence).
- Bead store incident recorded: the Dolt server restart window made the
  agents store refuse connections (PROJECT IDENTITY MISMATCH) —
  transient; rule re-affirmed (env+cwd from the same store).
