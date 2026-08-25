---
name: beads-orchestrator
description: "Orchestrator-only governance for Beads semantics and Gas Town dispatch. USE FOR: assigning lanes via gt sling, convoy/mountain batching, merge-queue oversight, dedup/supersede/re-parent of issues, claim convergence. DO NOT USE FOR: implementing a bead (beads-worker); standing audits (governance-audit)."
license: MIT
metadata:
  bundle: beads
  scope: universal
---

# Beads Orchestrator

## Claims Protocol

Only orch mutates issue semantics (`bd` CLI only, never hand-edit `.beads/`). One owner per objective; orch owns epic/feature/hotfix **roots**, workers get **child** Beads. 30-min abandonment: stale Bead/lane/WIP is FREE — claim and continue (`gt unsling`, `bd reclaim`).

## Dispatch — Gas Town Surface

```bash
gt ready                    # work available across town
gt sling <bead> [target]    # hook + start (auto-spawns polecat for rigs)
gt convoy create <ids>      # batch tracking; auto-closes when all land
gt mountain <epic-id>       # stage+launch epic waves (stall detection)
```

## Queue Oversight

```bash
gt mq list | status | retry <id>
gt convoy status            # progress, tracked issues, workers
```

Validator PASS on pushed SHA before integrate; GitFlow integrate only. Increment closes ONLY with empty residue + integration-lane run — see `verification/closure`.

## Semantic-Mutation Rules (bd)

1. Re-parent: `bd dep remove` then `bd dep add -t parent-child`.
2. Epics: `-t tracks` for epic→task ordering (not blocked-by-task).
3. Fix stale `status=blocked` via `bd update --status open` when deps cleared.
4. Fold = absorb loser DoD into survivor + close. Epic ≥70% done, ≤2 open children → drain; rewrite survivor description in same pass.

## Conflict Convergence

Re-read before every mutation batch; graph changed → STOP and re-audit. Detail: [references/conflicts.md](references/conflicts.md) · [references/consolidation.md](references/consolidation.md).

## Context Budget

Load: CORE + this + project AGENTS. Skip worker playbooks; domain law on marker.
