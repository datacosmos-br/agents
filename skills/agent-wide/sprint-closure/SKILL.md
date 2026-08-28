---
name: sprint-closure
description: 'increment closure, integration evidence, residue elimination'
metadata:
  aihub.tags: '["policy:atomic-effects","policy:causal-subprocess","policy:fail-loud","policy:no-fallback","policy:preflight-before-effects","policy:strict-execution","policy:zero-residue","provenance:agents-owned","role:governance","updates:manual","usage:router"]'
---

# Sprint Closure

Activate before an increment handoff, closure claim, integration merge, or final
residue audit. Read the [complete procedure](references/procedure.md) and keep
the increment open until its runtime, applicable gates, review, landing,
post-merge proof, and tracker contract all hold. During tracker suspension,
create no substitute tracker or ledger, preserve evidence only in separately
authorized Git/PR/CI, and keep the increment open.

External-token validations excluded before invocation are recorded as `NOT
EXECUTED` and do not block closure; they are never represented as green. Once
invoked, their raw credential or runtime failure blocks closure normally.
