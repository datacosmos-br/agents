---
name: sprint-closure
description: "End-of-sprint gate: EMPTY residue set (dead code, shims, un-rewired consumers/tests, open worktree/PR/Bead) + proof the increment runs on the integration lane. USE FOR: closing an increment. DO NOT USE FOR: per-change verification (verification-loop)."
bundle: verification
scope: universal
---

# Sprint Closure

Authority: `UNIVERSAL_CORE` Laws 29/4/21/28. Per-change gate: `verification/loop`; tracker semantics: `beads-orchestrator`.

## Scrum shape

Milestone → increment epics (ordered, hard deps) → child Beads. Each open Bead: one `lane:<name>`, one `increment:<epic-id>` in a release lane. Starts only when the previous is CLOSED; ships to the integration lane. Scope fixed at entry; discovered work filed (`-t discovered-from`) — never absorbed.

## Entry criteria

Previous increment CLOSED · integration lane clean (no drift, gates green) · every Bead owned with bounded path scope.

## Residue set — must be EMPTY (binary, per increment)

Scope = paths the increment touched. Each row is a command, not an opinion.

| Residue | Binary check |
| --- | --- |
| Dead code | Zero references to increment symbols across src+tests+consumers. |
| Compat code | Zero shim/alias/wrapper/fallback for old behavior. |
| Un-rewired consumers/tests | Callers on new contract; no tests of removed behavior. |
| Open worktree / PR / Bead | None left for this increment. |

Superseded code is DELETED in the cycle that replaces it — a deferred cleanup bead, TODO or promise IS the violation. State net LOC in the exit report; net-positive only for purely additive work. Cannot delete now → shrink the change.

## Running on the integration lane

Behavior exercised through its REAL public surface on the integration lane at the merged SHA (artifact captured), `verification/loop` completed there. `main` promotion stays operator-gated; never claim it as sprint proof.

## Exit report

Per increment: SHA, gates, residue table with command+result per row, net LOC for the cycle, real-surface artifact, Beads/PRs/worktrees closed. Any non-empty residue row = NOT closed: fix in-sprint or STOP and surface.
