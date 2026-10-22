---
name: codemod
description:
  "ast-grep codemod rules, generalized law, exact matching, rule tests, snapshots, make verbs"
metadata:
  aihub.tags: '["activation:detected","decision:ADR-0009","detect:dependency:python:flext-infra","detect:marker:sgconfig.yml","effective:2026-10-22","route:project","subject:ast-grep","usage:on-demand"]'
---

# codemod

Write and evolve the structural rules that `make mod` applies. The obligations come
from `rules/workflow/structural-migrations.md`: one generalized law per rule, layered,
and propagated. This skill is the authoring procedure.

The engine that runs the rules owns its schema, metadata keys, receipts and verbs. In
FLEXT that owner is flext-infra, documented in the workspace guide
`docs/guides/codemod-rules.md`. Read it before you write a FLEXT rule. The rule anatomy
and generalization techniques are in [authoring](references/authoring.md).

## Use for

- A repeated violation, rewire or migration that more than one call site shares.
- Widening an existing rule to cover a new variant of the same law.
- Merging rules that state one law with different literals.
- Testing, snapshotting and retiring rules through the repository verbs.

## Do not use for

- A unique edit at one site that no rule can express: edit it and state why.
- A finding inside a generated file: fix its generator or template, then regenerate.
- Applying a rule to a tree with raw `ast-grep scan --update-all`, `sg -U` or an
  engine module: only the repository's Make verbs apply rules.

## Procedure

1. **Search before writing.** Look in the catalog (rule ids, messages, shared `utils/`
   matchers) and in the text rules for a rule that already states the law. If one
   exists, widen its patterns or constraints instead of adding a sibling.
2. **State the law in one sentence**: the owner, the rejected shape, and the correct
   form. A rule that cannot be stated without naming one symbol or one file is a
   one-shot migration. Prefer a general law that the symbol is one instance of.
3. **Choose the layer.** Put the rule at the highest layer where the law holds: the
   engine package's universal catalog, then a framework layer, then the project overlay.
   A child layer only narrows; never copy a parent rule.
4. **Choose AST or text.** Code shapes use ast-grep. Text rules are for surfaces with no
   syntax tree, or for line-shaped declarations an AST rule cannot express. A text rule
   still needs an anchor, word boundaries and file scoping.
5. **Generalize, then make it exact.** Use the techniques in
   [authoring](references/authoring.md#generalize): `any:` over patterns, `constraints`
   on metavariables, shared `utils/` matchers, and owner-derived context instead of
   literal lists. Then anchor on node kinds, scope with `files`, and turn every known
   false positive into a `not:` clause.
6. **Prototype on a scratch copy.** `ast-grep scan --rule <file> <scratch-sample>` is
   research only. Run it on copied samples outside the repository, never on the tree
   you are changing.
7. **Test.** The rule test lists `valid` cases (near misses, one per exclusion) and
   `invalid` cases (every shape the law rejects). Regenerate snapshots only through the
   repository's snapshot verb, and review the snapshot diff in the same commit.
8. **Apply through Make.** Run the repository verb (`make mod`, `make mod-text`). It
   must reach a verified fixed point; a second run applies nothing. Run the affected
   tests after the rewrite and review the diff by class of change.
9. **Retire with the law.** When a law is superseded, delete its rule, test and
   snapshot in the same cutover that removes the law.

## Consolidation points

Review the catalog for these whenever you add or touch a rule:

- **Same law, different literals.** Two or more rules differ only by a module, symbol
  or call name. Merge them into one rule with a `constraints` regex or an owner-derived
  context predicate.
- **Same receiver guard repeated.** Several rules repeat one `inside`/`has` guard
  (an import check, a facade binding). Extract it once to `utils/` and reference it with
  `matches:`.
- **Detection and fix split.** A ban rule and a rewrite rule match the same shape.
  Keep the rewrite with a `fix:` and delete the ban.
- **One-shot migrations.** A text rule scoped to one file or one literal identifier.
  Once it applies nothing anywhere it targets, it is a retirement candidate under the
  repository's propagation policy.
- **Inexact rules.** Regex-only matching where a node kind exists, unanchored or
  cross-definition `.*?` text patterns, a missing `files` scope, or a `fix:` without a
  test. Each is a defect at the rule.

## Evidence

Record the rule id, the verb you ran, its applied and verified counts, and the test
results on the change. A rule change without a regenerated snapshot diff, or a rewrite
without a fixed-point receipt, is not finished.
