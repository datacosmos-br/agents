---
name: sprint-closure
description: "Use at an increment/sprint boundary before declaring it Done. USE FOR: all-or-nothing closure with empty residue set (dead code, shims, un-rewired consumers, open worktree/PR/Bead), proving the increment runs on the integration lane, net-LOC accounting. DO NOT USE FOR: per-change gating (verification-loop); tracker semantics (beads-orchestrator)."
license: MIT
metadata:
  bundle: verification
  scope: universal
---

# Sprint Closure

Authority: CORE Laws 29, 4, 21, 30. Per-change gate: `verification/loop`. Not restated here.

## Shape and entry

Milestone → increment epics (ordered) → child Beads with one `lane:<name>` each (`increment:<epic-id>` in a release lane). Starts only when the previous closed; ships to the integration lane, never a waiting branch. Scope fixed at entry; discoveries filed (`-t discovered-from`). Entry: previous CLOSED · lane clean · owner+scope on every Bead.

## Residue set — must be EMPTY (binary checks)

| Residue | Binary check |
| --- | --- |
| Dead code | Increment symbols with zero references anywhere |
| Shims/fallbacks | Zero compat paths for old behavior |
| Consumers/tests | Zero callers or tests on superseded contracts |
| Worktree/MR | No increment worktree; `gt mq list` clean |
| Convoy/hook/Bead | `gt convoy status`, `gt hook show`, children all closed |

Superseded code is DELETED in the replacing cycle — cleanup bead/TODO/"later" = the violation (Law 30). Refactor lands net-negative in LOC (`git diff --shortstat` in exit report) or not at all; net-positive only if purely additive — state it.

## Running on the integration lane

Real public surface exercised at the merged SHA (artifact captured); `verification/loop` green there. `main` promotion is operator-gated — never proof.

## Exit report

SHA, gates, residue table (command+result per row), net LOC, real-surface artifact, Beads/convoys/worktrees closed. Non-empty row = NOT closed: fix in-sprint or STOP.

## Context Budget

Load: CORE + this + `verification/loop`. Skip role playbooks unless held.
