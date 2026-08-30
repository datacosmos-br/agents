---
name: sprint-closure
description: 'increment closure, integration evidence, residue elimination'
metadata:
  aihub.tags: '["policy:atomic-effects","policy:causal-subprocess","policy:fail-loud","policy:no-fallback","policy:preflight-before-effects","policy:strict-execution","policy:zero-residue","provenance:agents-owned","role:governance","updates:manual","usage:router"]'
---

# Sprint Closure

Activate before an increment handoff, closure claim, integration merge, or final
residue audit. Read the `complete procedure` (skill file) and keep
the increment open until its runtime, applicable gates, review, landing,
post-merge proof, and tracker contract all hold. During tracker suspension,
create no substitute tracker or ledger, preserve evidence only in separately
authorized Git/PR/CI, and keep the increment open.

Review and check closure is part of the increment: locate unresolved review
threads and failing checks with
`skills/tool/pr-sheriff/scripts/pr_triage.py` (pr-sheriff), answer each with
runtime evidence, and land before claiming closure.

External-token validations excluded before invocation are recorded as `NOT
EXECUTED` and do not block closure; they are never represented as green. Once
invoked, their raw credential or runtime failure blocks closure normally. This
exclusion applies only to the unavailable workflow: every independently
observed alert, finding, open PR, or other actionable residue remains blocking
until corrected and freshly revalidated. Never label work complete while also
listing such pending work. A broken or incomplete version never ships:
`rules/workflow/production-readiness.md` (rule file) owns adoption of every
defect in the increment's blast radius, including pre-existing ones.
