---
description:
  Structural migration rules are maximally generalized, layered, and propagate through
  project imports.
metadata:
  aihub.tags: '["decision:ADR-0009","effective:2026-11-02","route:both"]'
---

# Structural migration rule hierarchy and propagation

Structural migrations use the selected repository's native catalog and existing engine
owner under `rules/workflow/canonical-commands.md`; this global rule declares no
project-specific verb. Raw tools or engine modules never substitute for that surface.
Use native constraints, shared utilities and transforms under
`rules/workflow/declared-tool-ownership.md`; prove semantic convergence.

Rules are engineering law, not a per-defect catalog: each rule states
one generalized law and names the principle it enforces. A new violation is first
checked against an existing rule's scope; only a genuinely new law earns a new rule.
Per-key literal patterns that express the same single-owner, residue, or fail-loud law
are consolidated into one rule with explicit file scoping.
Minimize executed rules by consolidating the same law, not by disabling coverage.
Retire one-shot migration rules only after the complete consumer census proves zero
residue; keep ongoing invariants. Record counts through the existing typed rule catalog.

Every rule ships with a test of `valid` and `invalid` cases and the snapshot the
repository's snapshot verb writes. A rewrite reaches a verified fixed point. A rule
whose law is superseded is deleted with its test and snapshot in the same cutover. The
`codemod` skill owns authoring procedure for ast-grep catalogs; the selected engine's guide
owns its schema and verbs.

## Every pattern fix becomes one automatic rule

Convergence is continuous and rule-driven (operator orders 2026-11-02, tracker memory
`operator-order-2026-11-02-structural-patterns-automatic`, verbatim excerpt: "isso tem
que ser arrumado de forma automatica, ajustado e rápido, nao podemos ficar tolerando
falhas como essas"):

- A pattern fix found by the operator or any agent, including one applied by hand, is
  not finished until it exists as an automatic rule of the selected engine's catalog.
  A recurring shape corrected manually is a defect; write the rule and re-apply it.
- A small batch is one rule, that is one law, applied at fleet scale at a time. Manual
  per-file edits are never the batch. Validation and application of that rule run
  through the owner's scoped command under `rules/workflow/canonical-commands.md`
  ("Scoped validation of one change").
- Exactly one rule per law: duplicate or diverging rules for the same law are
  consolidated at the highest applicable layer in the same change.
- Rule output needs zero manual follow-up: the rewrite reaches its fixed point and
  passes the gates with no secondary fixer, formatter or hand edit.
- Detection is exact: every violating site is found and no legitimate site is touched,
  proven against the complete census with the expected match cardinality.
- The engine is fast and runs on every root: branch, worktree, member and external
  consumer, with no assumption about a particular checkout layout.
- Any violation of a foundational pattern is a disaster, fixed first at its owner
  (rule, generator or engine) before other work, never tolerated or deferred.

Rules are hierarchical. The canonical governance owner holds provider-neutral law. The engine package
owns executable implementations and their schema; consumers receive declared
projections, not a competing governance owner. Its universal layer holds context-free
patterns. A framework layer holds only
framework-specific patterns in that framework's law surface. A project overlay holds
only project patterns in the project tree. A child layer strengthens its parents with
narrower constraints and never re-allows what a parent rejects; duplicated patterns
across layers are defects consolidated at the highest applicable layer in the same
change.

Rules propagate through imports. When a project imports another, the importing project
receives the imported project's rule layer through the selected canonical delivery
owner, and its migration config references those layers by their delivered paths.
Delivery regenerates consumer copies with their standardized generated headers;
hand-edited copies are defects. Delivery does not authorize resuming suspended
orchestration; composition follows the current `rules/coordination/gascity.md` boundary.
