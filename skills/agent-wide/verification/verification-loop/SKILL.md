---
name: verification-loop
description: 'completion evidence, runtime verification, native gates'
license: MIT
metadata:
  aihub.tags: '["decision:plan-00","effective:2026-09-03","policy:atomic-effects","policy:causal-subprocess","policy:fail-loud","policy:no-fallback","policy:preflight-before-effects","policy:strict-execution","policy:zero-residue","provenance:agents-owned","role:verification","updates:manual","usage:router"]'
  version: 1.1.0
---

# Verification Loop

Review claims about PR threads and checks are gated evidence too: locate
unresolved threads and failing checks with
`skills/tool/pr-sheriff/scripts/pr_triage.py` (pr-sheriff) before repeating
them as status.
Activate after behavior changes and before any pass, resolution, readiness, or
completion claim. Read the `complete procedure` (skill file), prove
the smallest real runtime first, and then run the repository-owned gates for the
affected scope. Later edits invalidate earlier evidence where their scopes
overlap. Production readiness adopts every defect in the blast
radius, including pre-existing ones; read
`rules/workflow/production-readiness.md` (rule file) before any completion
claim over a red or unresolved base.
When the repository owns the deployed runtime, completion also requires
installing or reconciling that runtime from the merged integration SHA and
proving the public surface there.
