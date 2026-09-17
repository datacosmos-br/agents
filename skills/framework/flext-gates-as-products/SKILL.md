---
name: flext-gates-as-products
description: 'flext gates-as-products, budget rows, registry vocabularies, atomic primitives, config keys'
license: canonical flext law
metadata:
  aihub.tags: '["activation:detected","decision:ADR-0015","detect:dependency:python:flext-infra","detect:selected-tag:flext","effective:2026-09-11","route:project","subject:flext","usage:on-demand"]'
---

# FLEXT Gates as Products

Composes with `$flext-law`, `consumption-law.md` (ADR-015) and rule
`gate-registry-ownership.md`; owns only the enforcement-product delta.

## Gate product law

- Every gate is a product: one typed config namespace under
  `[tool.flext.project.<gate>]` (thresholds/fields are data under config
  SSOT, never constants-only), a registry row (`SARIF_TOOL_INFO`,
  `ALLOWED_GATES`), a gate-class entry, and — for R4 budgets — a required
  budget row (`time-seconds`, `memory-mb`, `tokens`) in
  `[tool.flext.project.budget]` per gate id.
- Registry divergence (class without vocabulary row, vocabulary without
  class, two classes claiming one id) fails the registry build before any
  gate runs; never a silent unreached gate.
- Gate thresholds belong to `[tool.flext.project.*]` or `config/codegen.yaml`;
  constants may seed defaults, but hand-edited per-consumer values route
  through the config projection (`make gen`, fixed point proven).
- Rollout: new strict gates start advisory (warn) for one cycle, then hard
  (operator stabilization law 2026-09-08); baselines of findings are tracker
  evidence, never committed fixtures.

## Atomic primitives (core `u` ownership)

- File mutation primitives are owned ONCE by `flext-core`
  (`u.FlextUtilitiesFiles`): `append_atomic` (O_APPEND + O_CREAT, typed
  `r[int]`), `write_atomic` (temp + rename). Members consuming
  `u.Cli.atomic_write_*` migrate and delete the duplicates (net-negative).
- Production usage: path trust (`O_NOFOLLOW`), durability (`fsync` before
  rename for the write path), EINTR-safe write loops, umask-respecting
  modes via constants — never bare defaults silently partial.

## Consumer grammar (R1) detector pattern

- Roots from the runtime family surface (`core_u.project_alias_owners()`).
- Legal iff `X in root.__all__`; any `pkg.<submodule>` or wildcard violates;
  same-root assembly exempt. Statements carry the true `lineno` and derive
  hints from the derived rename map.

## Budget telemetry

- Gate runner records measured duration per gate execution into the
  GateExecution/report; budgets compare measured reality, not intended
  limits, before a workspace may claim green.

## Automation cycle (canonical verbs, codified 2026-09-11)

FLEXT program work runs this loop per slice; never ad-hoc tool calls.

1. Preflight + generation: `make gen` at the lane root (config SSOT
   → projections) before any semantic rewrite.
2. Semantic mutation: `make mod` — the engine runs ast-grep rules, fixed-point
   application, Ruff, Pyrefly, and real LSP diagnostics in one selector-free
   verb. The engine derives scope from repository state; callers do not invent
   module or namespace selectors.
3. Cycle hygiene: `make fix` → `make fmt` → `make check` → `make test` with
   canonical persistent testmon; the declared full-suite verb owns expansion.
4. Graph evidence through the agent-side `code-review-graph` CLI, operated
   exactly as `$crg` defines (freshness gate, lane graph, verified verbs);
   flext code never imports it — the CRG library-boundary ban rule. FLEXT
   delta only:
   - the workspace root is a superproject: its graph is built with the
     submodule recursion `$crg` prescribes, and each member lane checkout
     keeps its own graph;
   - `impact --files` / `detect-changes` output is blast-radius evidence on
     tracker items and PR reviews, never gate evidence;
   - `dead-code --json` per member feeds R2 zero-residue sweeps only after
     source confirmation;
   - `refactor rename|suggest` previews are applied only by `make mod`
     (Rope/ast-grep owner), then the cycle above revalidates.
5. Commit scoped → push FF → PR → `--no-ff` into the declared integration
   branch → gates on the merged SHA → graph refresh on the integrated tip
   (`$crg` runbook) → tag / release only then (F5 law).

Rule archives (never hand-invent a new authority):

- Repository rules: `flext-infra/src/flext_infra/codemod/rules/*.yml`
  (100+ curated; ADR-014 governs).
- Agent-global rules: the ast-grep universal rules archive projected under the
  agent rules directory and consumed only through the repository's canonical
  Make owner. It applies to cross-repo agent-side artifacts; repository law
  stays in the repository engine.
