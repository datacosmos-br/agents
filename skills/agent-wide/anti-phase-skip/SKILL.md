---
name: anti-phase-skip
description: 'Enforce the complete phase lifecycle when work moves toward integration or closure.'
bundle: governance
scope: universal
license: MIT
metadata:
  aihub.tags: '["provenance:agents-owned","role:governance","updates:manual","usage:router"]'
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
blocked phase must be reported loudly in the final response; it may never be
renamed as completed or replaced by a manual ledger.
