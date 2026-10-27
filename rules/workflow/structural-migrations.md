---
description:
  Structural migration rules are maximally generalized, layered, and propagate through
  project imports.
metadata:
  aihub.tags: '["decision:ADR-0009","effective:2026-10-25","route:both"]'
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
selected structural-migration skill owns authoring procedure; the engine owner's guide
owns its schema and verbs.

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
