---
name: verification-loop
description: "completion evidence, runtime verification, native gates"
license: MIT
metadata:
  aihub.tags: '["decision:ADR-0038","effective:2026-11-03","usage:router"]'
  version: 2.0.0
---

# Verification Loop

Before claiming that a change works, is done or is ready, prove it on the smallest real
runtime (`rules/law.md` law 9), then run the repository's declared gates for the touched
scope (`rules/workflow/canonical-commands.md`).

- Each claim carries law 1 evidence from this turn; a run that executed nothing is not a
  pass.
- The first failure is the result: fix its cause and rerun from the runtime proof; law 6
  owns the one red-base exception.
- A later edit voids earlier evidence for the scope it touches.
- Each boundary (resume, before code, commit, merge) starts from live state: the
  integration tip merged into the lane and the owner's source read; a snapshot,
  brief or memory is a lead, never evidence. Under host load the work continues on
  light verbs; it never waits and never shortcuts a gate.
- A hook's refusal is a failing gate and is never bypassed (law 8).
- Done means landed under law 10 and `rules/git/gitflow-branch-pr.md`; local green or an
  open pull request is in progress.
