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
  `[tool.flext.project.<gate>]` (thresholds/fields are data under config SSOT,
  never constants-only), a registry row (`SARIF_TOOL_INFO`, `ALLOWED_GATES`), a
  gate-class entry, and a required R4 budget row (`time-seconds`, `memory-mb`,
  `tokens`) under `[tool.flext.project.budget]` for every gate id.
- Registry divergence fails the registry build before any gate runs.
- Thresholds belong to project config; consumer overrides flow through the
  projection owner and `make gen` fixed-point proof.
- Strict gates move from advisory to hard only through the declared rollout;
  finding baselines remain tracker evidence, never fixtures.

## Atomic primitives

- `flext-core` owns file mutation once through `u.FlextUtilitiesFiles`.
- Production writes preserve path trust, durability, EINTR safety, and
  umask-respecting modes; consumers delete duplicate primitives when rewired.

## Consumer grammar

- Roots come from the runtime family surface.
- An exported symbol is legal only through the owner's public `__all__`;
  private submodules and wildcards violate, while same-root assembly is exempt.

## Budget telemetry

- Gate reports record measured duration and compare measured reality with the
  declared budget before a workspace may claim green.

## Automation cycle

FLEXT program work uses only selector-free root Make verbs.

1. Run `make gen` at the lane root before semantic rewrites.
2. Run `make mod`; the engine owns ast-grep, fixed point, Ruff, Pyrefly, and LSP
   diagnostics and derives scope from repository state.
3. Run `make fix`, `make fmt`, `make check`, and canonical test verbs with the
   persistent testmon database.
4. Use `$crg` only for fresh graph evidence. The workspace root uses recursive
   submodule indexing and every member lane keeps its own graph. Impact and
   change detection are review evidence, never gate substitutes. Confirm
   dead-code candidates in source. Refactor previews are applied only through
   `make mod`, then the cycle revalidates.
5. Commit scoped work, push FF, open a PR, merge `--no-ff` into the declared
   integration branch, rerun gates on the merged SHA, refresh graphs, and only
   then tag or release.

Rule archives are owners, never copy sources:

- Repository codemod rules live under flext-infra's declared rules owner.
- Agent-global rules are projected under the agent rules directory and consumed
  only through the repository Make owner.
