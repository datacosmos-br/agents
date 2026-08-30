---
name: safe-delete
description: 'safe deletion, atomic obsolete-code extermination, artifact retirement, recovery evidence'
license: MIT
metadata:
  aihub.tags: '["policy:atomic-effects","policy:causal-subprocess","policy:fail-loud","policy:no-fallback","policy:preflight-before-effects","policy:strict-execution","policy:zero-residue","provenance:agents-owned","role:governance","updates:manual","usage:on-demand"]'
  version: 2.0.0
---

# Safe Delete

Delete only exact, owned targets with an explicit recovery contract. This skill also applies when an approved cutover supersedes tracked code: the replacement, consumer rewire, and deletion are one atomic change, never a compatibility or rollback sequence. Follow the complete [router procedure](references/router-procedure.md) and preserve its owners, evidence contracts, failure propagation, and required output standard.
