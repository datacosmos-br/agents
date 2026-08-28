---
name: beads-orchestrator
description: 'Govern Beads dependencies and ownership when tracker orchestration is explicitly authorized.'
bundle: beads
scope: universal
metadata:
  aihub.tags: '["activation:opt-in","detect:opt-in:beads-orchestration","provenance:agents-owned","route:agent","tool:beads","updates:manual","usage:router"]'
---

# Beads Orchestrator

## Authority

See `UNIVERSAL_CORE` roles; `governance/rules` §Tracker / §Role. Only orch mutates issue semantics; `bd` CLI only; never hand-edit `.beads/`.

## Claims Protocol

`assignee` = ownership. One operational owner per objective; never touch another owner's lane.

## Lane control

- Staleness is a finding, never abandonment proof. Preserve the lane and confirm
  ownership through the canonical tracker before claiming or continuing it.
- Ownership shape: orch owns epic/feature/hotfix/bugfix **root**; workers get **child** Beads.
- Use the configured execution identity. A failed attempt remains red and never
  triggers automatic model, tier, or provider switching.
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
