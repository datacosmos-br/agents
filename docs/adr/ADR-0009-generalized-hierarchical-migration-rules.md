# ADR-0009: Generalized hierarchical structural-migration rules

## Status

Accepted — 2026-09-05

Amended — 2026-10-25: native capability reuse, minimal rule execution and project scope.

Amended — 2026-10-31: universal Python layer owner and retirement of this repository's
overlay.

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
7. The flext-infra catalog is the universal layer for Python codemod rules. This
   repository keeps only its own overlay; its rules are neither universal nor FLEXT and
   agents-governance owns them. An overlay rule, when one exists, lives under
   `config/rules/ast-grep/` and ships in the wheel.
8. An invariant the bundle loader already validates is enforced by the loader, not by a
   parallel rule. The happy-path fixture law (`require-basic-usage-fixture`) is enforced
   by the evaluation loader: a `happy_path` task without `inputs.files` fails loud naming
   its path.

## Consequences

The evaluation-suite rule corpus consolidated from 24 files to 7 (one generalized
owner-policy rule plus hygiene, outcome, and fixture rules). New legacy key shapes are
covered by the generalized rule without new files. Projects across the fleet receive the
universal layer through delivery instead of copying it.

On 2026-10-31 the remaining seven rules, misnamed `universal`, were retired. A census
under `make mod-check` found zero matches. Six were one-shot migrations:
`no-owner-owned-policy-in-suites`, `no-partial-eval-metric`,
`no-task-completed-outcome`, and the three deletion-whitespace rules. Each was deleted
with its test and snapshot. The owner-policy rule also deleted a `version:` key that the
loader accepts, so retiring it removes that conflict. The fixture rule moved into the
loader (decision 8). The repository now has no ast-grep overlay, no `sgconfig.yml` and
no snapshot whitespace exception. `make mod` and `make mod-check` keep only the
evaluation YAML normalization.

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

The 2026-10-31 amendment records operator rulings D1 and D2. Their words are kept under
`operator-ruling-2026-10-31-agents-astgrep-overlay` in the selected agents tracker, and
the execution is tracked by bead `ag-edq0`.
