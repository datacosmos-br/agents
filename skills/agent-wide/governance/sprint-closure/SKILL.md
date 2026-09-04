---
name: sprint-closure
description: 'increment closure, integration evidence, residue elimination'
metadata:
  aihub.tags: '["decision:plan-00","effective:2026-08-30","policy:atomic-effects","policy:causal-subprocess","policy:fail-loud","policy:no-fallback","policy:preflight-before-effects","policy:strict-execution","policy:zero-residue","provenance:agents-owned","role:governance","updates:manual","usage:router"]'
---

# Sprint Closure

Activate before an increment handoff, closure claim, integration merge, or final
residue audit. Read the `complete procedure` (skill file) and keep
the increment open until its runtime, applicable gates, review, landing,
post-merge proof, and tracker contract all hold. During tracker suspension,
create no substitute tracker or ledger, preserve evidence only in separately
authorized Git/PR/CI, and keep the increment open.

The landing row is satisfied only by a no-ff merge commit on the repository's
declared integration branch, followed by fresh affected gates and runtime
evidence from that merged state. An open PR, green local lane, mergeable status,
or feature-branch deployment never satisfies closure. If no independent
reviewer exists, closure may substitute the approval row only after the operator
explicitly authorizes an administrative merge; every other row remains
mandatory and evidence records the approval as operator-authorized.

Review and check closure is part of the increment: use `pr-sheriff`, resolve AI
Hub forge state only after the repository profile selects the managed-private
contract, and collect direct GitHub evidence for unresolved review threads and
failing checks. Answer each with runtime evidence and land before claiming
closure. Never invoke a removed helper or direct Python script.

External-token validations excluded before invocation are recorded as `NOT
EXECUTED` and do not block closure; they are never represented as green. Once
invoked, their raw credential or runtime failure blocks closure normally. This
exclusion applies only to the unavailable workflow: every independently
observed alert, finding, open PR, or other actionable residue remains blocking
until corrected and freshly revalidated. Never label work complete while also
listing such pending work. A broken or incomplete version never ships:
`rules/workflow/production-readiness.md` (rule file) owns adoption of every
defect in the increment's blast radius, including pre-existing ones.
