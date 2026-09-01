---
description: Authority order and recency precedence
metadata:
  aihub.tags: '["decision:plan-12","effective:2026-08-30","route:both"]'
---

# Authority order and recency precedence

Authority order: operator request > declared orchestration contract > canonical
tracker > ADRs > skills > docs > defaults.

Recency resolves conflict inside the same authority level: the newer plan
imposes the stronger orientation. The newer artifact is the one with the higher
`effective:` approval date, or the one that declares `supersedes:` over the
older. Typed runtime (`src/agents_governance/approvals.py`) owns the tag
formats and resolution; every approval reference resolves physically into
`docs/`, and one that does not resolve fails loud. Historical artifacts are
evidence only: a superseded plan, ADR, or sealed record is never reactivated
or edited to compete with its replacement. On conflict, adjust the lower or
older artifact to match; never override the operator to satisfy stale
guidance.

While orchestration and tracker runtimes are suspended, do not invoke them.
Create no substitute tracker or ledger, preserve implementation evidence only
in separately authorized Git/PR/CI surfaces, and leave phase closure open.

Exact operator authorization naming targets, disposition, recovery, and
validation survives interruption, divergence, and red gates; re-preflight and
continue. Ask only when the effect expands beyond it or two evidenced current
intentions conflict. State alone proves no intention, actor, or process.
