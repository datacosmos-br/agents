---
description:
  Structural migration rules are maximally generalized, layered, and propagate through
  project imports.
metadata:
  aihub.tags: '["decision:ADR-0009","effective:2026-09-05","route:both"]'
---

# Structural migration rule hierarchy and propagation

Structural migrations run through the repository's declared structural verbs (`make mod`
and the rule-test, snapshot and text-rule verbs its `make help` lists), powered by
ast-grep. Raw `ast-grep scan --update-all`, `sg -U` or an engine module never applies a
rule to a tree. Rules are engineering law, not a per-defect catalog: each rule states
one generalized law and names the principle it enforces. A new violation is first
checked against an existing rule's scope; only a genuinely new law earns a new rule.
Per-key literal patterns that express the same single-owner, residue, or fail-loud law
are consolidated into one rule with explicit file scoping.

Every rule ships with a test of `valid` and `invalid` cases and the snapshot the
repository's snapshot verb writes. A rewrite reaches a verified fixed point. A rule
whose law is superseded is deleted with its test and snapshot in the same cutover. The
`ast-grep-codemod` skill owns the authoring procedure; the engine owner's guide owns its
schema and verbs.

Rules are hierarchical. The universal layer is the catalog the rule engine's own package
ships to every consumer and holds context-free patterns. A framework layer holds only
framework-specific patterns in that framework's law surface. A project overlay holds
only project patterns in the project tree. A child layer strengthens its parents with
narrower constraints and never re-allows what a parent rejects; duplicated patterns
across layers are defects consolidated at the highest applicable layer in the same
change.

Rules propagate through imports. When a project imports another, the importing project
receives the imported project's rule layer through the canonical governance delivery of
its rig, and its migration config references those layers by their delivered paths.
Delivery regenerates consumer copies with their standardized generated headers;
hand-edited copies are defects.
