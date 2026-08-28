---
name: anti-phase-skip
description: 'phase lifecycle, runtime validation, integration closure'
license: MIT
metadata:
  aihub.tags: '["policy:atomic-effects","policy:causal-subprocess","policy:fail-loud","policy:no-fallback","policy:preflight-before-effects","policy:strict-execution","policy:zero-residue","provenance:agents-owned","role:governance","updates:manual","usage:router"]'
  version: 1.0.0
---

# Anti Phase Skip

Skipping a phase cycle is a critical delivery defect. It creates false DONE
claims, unmerged behavior, stale validation, open tracker state, abandoned WIP,
and runtime failures that green unit tests cannot expose.

Activate before changing tasks, advancing a plan phase, handing off, or claiming
completion. Read the [complete procedure](references/procedure.md).

A phase cannot be DONE until implementation, real runtime, native gates,
integration update, commit, push, approved and merged PR, post-merge runtime,
zero residue, and canonical tracker closure all have fresh evidence. Missing one
step keeps the same phase open.

Only an explicit operator decision may pause, reorder, or replace a phase. A
failed check, actionable review, open PR, pending approval, or merge conflict is
work inside the phase: fix, publish, revalidate, and continue through landing.
Report and request help only after every authorized correction is exhausted and
the remaining condition is external or requires new authority. During tracker
suspension, create no substitute tracker or ledger, preserve evidence only in
separately authorized Git/PR/CI, and keep closure unavailable.
