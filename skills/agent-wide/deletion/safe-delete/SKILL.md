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

Delete only exact, owned targets with an explicit recovery contract. For tracked source,
Git history is that contract: exterminate superseded, excessive, wrong or duplicated code
without backups or hesitation, per the `zero residue` rule's "Exterminate without fear"
section. This skill also applies when an approved cutover supersedes tracked code: the
replacement, consumer rewire, and deletion are one atomic change, never a compatibility
or rollback sequence; an old public signature that still has consumers follows the
`zero residue` rule's "Deprecated-signature window" section until its census reaches
zero. Its caution is for untracked, foreign, live or
ownership-ambiguous state that Git cannot restore.
Follow the complete `router procedure` (project file) and preserve its owners, evidence
contracts, failure propagation, and required output standard.
