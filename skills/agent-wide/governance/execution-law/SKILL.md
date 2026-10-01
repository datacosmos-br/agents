---
name: execution-law
description: "sole-executor engagement, startup census, coordinator ladder, adoption, extermination, landing"
metadata:
  aihub.tags: '["decision:ADR-0032","effective:2026-10-01","usage:router"]'
  version: 1.0.0
---

# Execution law

Activate at the start of a sole-executor engagement — executing, cleaning up,
finalizing, or hardening a plan under a monopoly directive — and at every
phase boundary inside it. This router composes existing owners and declares
no new conduct. Read the `engagement procedure` (skill file) and apply it.

Composition order, fail closed:

1. The inviolable law prelude, then `make-check` for every command and gate.
2. Resolve the coordinator through `rules/coordination/coordinator-ladder.md`
   before the first coordinated effect; declare the lane per
   `rules/coordination/lane-ownership-declaration.md`.
3. Open with the `rules/coordination/session-startup-census.md` census; the
   project's wip verbs own lane state.
4. For structural change compose `$search-first`, `$yagni`, `$ssot`,
   `$solid`, `$simplify`, then conditional `$dry`.
5. The project's declared domain law — located through its provider router
   or nearest instructions file — owns every project-specific pattern; this
   skill never substitutes for it.
6. At every completion boundary, `$verification-loop`; at closure,
   `$sprint-closure` and `$release-closeout`.

Concurrent work is adopted fix-forward per
`rules/coordination/fix-forward-collaboration.md`; the monopoly assumption
yields to evidence, never to blame. Stop only for an authority conflict or a
destructive action: one precise question, per
`rules/coordination/operator-precedence.md`.
