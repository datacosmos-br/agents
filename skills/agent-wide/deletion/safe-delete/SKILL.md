---
name: safe-delete
description:
  "safe deletion, atomic obsolete-code extermination, artifact retirement, recovery
  evidence"
license: MIT
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-10-01","usage:on-demand"]'
  version: 2.0.0
---

# Safe Delete

Delete only exact, owned targets with an explicit recovery contract. This skill also
applies when an approved cutover supersedes tracked code: the replacement, consumer
rewire, and deletion are one atomic change, never a compatibility or rollback sequence.
An old public signature with remaining consumers follows the `zero residue` rule's
"Deprecated-signature window" section until its consumer census reaches zero.
Follow the complete `router procedure` (project file) and preserve its owners, evidence
contracts, failure propagation, and required output standard.
