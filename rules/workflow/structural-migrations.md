---
description: Structural migration rules are maximally generalized, layered, and propagate through project imports.
metadata:
  aihub.tags: '["decision:ADR-0009","effective:2026-09-05","route:both"]'
---

# Structural migration rule hierarchy and propagation

Structural migrations run through the canonical `make mod` / `make mod-check`
surface powered by ast-grep. Rules are engineering law, not a per-defect
catalog: each rule states one generalized law and names the FLEXT principle it
enforces. A new violation is first checked against an existing rule's scope;
only a genuinely new law earns a new rule. Per-key literal patterns that
express the same single-owner, residue, or fail-loud law are consolidated into
one rule with explicit file scoping.

Rules are hierarchical. The universal layer lives in the governance home and
holds context-free patterns. A framework layer holds only framework-specific
patterns in that framework's law surface. A project overlay holds only project
patterns in the project tree. A child layer strengthens its parents with
narrower constraints and never re-allows what a parent rejects; duplicated
patterns across layers are defects consolidated at the highest applicable
layer in the same change.

Rules propagate through imports. When a project imports another, the
importing project receives the imported project's rule layer through the
canonical governance delivery of its rig, and its migration config references
those layers by their delivered paths. Delivery regenerates consumer copies
with their standardized generated headers; hand-edited copies are defects.
