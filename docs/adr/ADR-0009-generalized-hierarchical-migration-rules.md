# ADR-0009: Generalized hierarchical structural-migration rules

## Status

Accepted — 2026-09-05

Amended — 2026-10-25: native capability reuse, minimal rule execution and project scope.

## Context

The `make mod` / `make mod-check` surface accumulated one narrow ast-grep rule per
historical defect shape (24 rules, most matching single literal keys of legacy
evaluation schemas). Per-key catalogs scale linearly with history, duplicate one law
across many files, and do not travel across projects, so importing projects could not
receive the migration law of the projects they import.

## Decision

1. Rules are generalized laws, not defect catalogs: one rule per engineering principle (single
   ownership, zero residue, fail-loud completeness, declared public fixtures), with file
   scoping expressed in the rule.
2. Rules are layered. The canonical governance owner holds provider-neutral law; engine packages own
   executable rule implementations and schemas. Their context-free layer, framework
   layers and project overlays compose without competing writable copies. Children
   strengthen; never re-allow.
3. Rules propagate through project imports via canonical governance delivery: importing
   projects reference imported layers from their migration config through the selected
   canonical delivery owner. Consumer copies are generated projections with standardized
   headers; delivery does not select or reactivate orchestration.
4. The existing engine owner consumes native analysis, invalidation and refactoring
   capabilities through typed generic interfaces. A second parse, index or traversal
   that duplicates an available native capability is removed after public semantic
   equivalence is proven. Runtime profiles establish costs before optimization.
5. Minimize executed rules by unifying equivalent laws using native rule features;
   preserve coverage and valid/invalid cases. Retire one-shot migrations after a complete
   consumer census, retaining ongoing invariant enforcement. Catalog-owned measurements
   record the actual rule count.
6. The global contract is
   [structural migrations](../../rules/workflow/structural-migrations.md).
   Repository catalogs own verb names; project law owns adapter placement and facade
   shape. FLEXT-specific tool names, paths and limits are not universal rules.

## Consequences

The evaluation-suite rule corpus consolidated from 24 files to 7 (one generalized
owner-policy rule plus hygiene, outcome, and fixture rules). New legacy key shapes are
covered by the generalized rule without new files. Projects across the fleet receive the
universal layer through delivery instead of copying it.

## Approval

Operator directive, 2026-09-05: structural-migration rules must be maximally generalized
under standard FLEXT rules, hierarchically defined, and carried to importing projects.

The 2026-10-25 amendment reconciles the operator's current native-tool, CA/DI and
generalized-rule orders, recorded under
`operator-order-2026-10-25-max-decoupling-ca-di` and
`operator-order-2026-10-25-rules-generalized-min-count` in the selected FLEXT tracker.
It supersedes this global rule's copied FLEXT command inventory and library-specific
implementation assumptions. Acceptance still requires the affected consumer and native
gates; this decision is not an implementation or delivery receipt.
