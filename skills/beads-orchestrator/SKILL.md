---
name: beads-orchestrator
description: Orchestrator-only Beads semantic governance — consolidation, re-parenting, dedup, supersede, migration, sequencing, conflict convergence. Use when organizing the tracker, mutating issue semantics, or preparing the graph before GitHub sync. Workers load beads-worker; auditors load governance-audit.
bundle: beads
scope: universal
---

# Beads Orchestrator

## Authority

See `UNIVERSAL_CORE` roles; `governance/rules` §Tracker / §Role. Only orch mutates issue semantics; `bd` CLI only; never hand-edit `.beads/`.

## Claims Protocol

`assignee` = ownership. One operational owner per objective; never touch another owner's lane.

## Lane control

- 30-min abandonment: stale Bead/lane/worktree/PR/WIP is FREE — claim and continue.
- Ownership shape: orch owns epic/feature/hotfix/bugfix **root**; workers get **child** Beads.
- Lightweight-first: cheapest tier for mechanical work; escalate after one failed light attempt.
- Validator PASS on pushed SHA before integrate. GitFlow integrate only; null merges are not shortcuts.
- Increment/sprint boundary: close only with an EMPTY residue set + integration-lane run. Never carry over. See `verification/closure`.

## Semantic-Mutation Rules (bd)

1. Re-parent: `bd dep remove` then `bd dep add -t parent-child`.
2. Epics: `-t tracks` for epic→task ordering (not blocked-by-task).
3. Fix stale `status=blocked` via `bd update --status open` when deps cleared.
4. Fold = absorb loser DoD into survivor + `bd close --reason`. Epic ≥70% done, ≤2 open children → drain.
5. Rewrite survivor description in the same pass.

## Conflict Convergence

Re-read before every mutation batch; if graph changed, STOP and re-audit. Detail: [references/conflicts.md](references/conflicts.md), [references/consolidation.md](references/consolidation.md).

## Context Budget

Load: UNIVERSAL_CORE + this skill (+ project AGENTS). Skip: worker playbooks; domain law unless marker active.
