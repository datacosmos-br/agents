# Sprint Closure

## Authority

`UNIVERSAL_CORE` Law 29 (all-or-nothing), 4 (one owner, no old+new), 21 (finish to
Done), 28 (complete cutover). Per-change gate: `verification/loop`. Tracker
semantics: `beads/orchestrator`. Not restated here.

## Scrum shape

Milestone → increment epics (ordered, hard deps) → child Beads. Every open Bead
carries exactly one `lane:<name>` and, inside a release lane, one
`increment:<epic-id>`. An increment is a SPRINT: it starts only when the previous
one is closed, and it ships to the integration lane — not to a branch that waits.

Scope is fixed at entry. New work discovered mid-sprint is filed
(`-t discovered-from`) and assigned to an increment — never silently absorbed,
never deferred to "later".

## Entry criteria

1. Previous increment CLOSED (this contract satisfied, not asserted).
2. Integration lane clean: no uncommitted drift, no unpushed commits, gates green.
3. Every Bead in the increment has an owner and a bounded path scope.

## Residue set — must be EMPTY (binary, per increment)

Each item is a command, not an opinion. Scope = paths the increment touched.

| Residue | Binary check |
| --- | --- |
| Dead code | Symbols added/left by the increment with zero references across src + tests + consumers (structural search, not grep-only). |
| Compatibility code | Zero shim/alias/wrapper/fallback/`deprecated` path introduced or retained for the old behavior. |
| Un-rewired consumers | Every caller of a changed contract uses the new one; zero references to the superseded symbol remain. |
| Un-rewired tests | Zero test asserts the removed behavior or imports a deleted path; tests exercise the public surface. |
| Open worktree | No lane worktree for this increment still registered. |
| Open PR | No PR for this increment still open; merged or closed with reason. |
| Open Bead | No child Bead of the increment still open/in_progress. |

Superseded code is DELETED in the same cycle that replaces it. "Kept until later"
is old+new coexistence (Law 4) — a defect, not a transition.

**Deletion cannot be deferred (Law 30).** Filing a cleanup bead, a TODO, a
comment or a follow-up sprint to delete later does not satisfy any row above —
that promise IS the violation. A refactor lands net-negative in LOC or it does
not land: measure `git diff --shortstat` for the cycle and state the number in
the exit report. Net-positive is allowed only when the increment is purely
additive (new capability, no replacement) — say so explicitly and name what it
replaced, or nothing. Cannot delete now → the change is too big: shrink it.

## Running on the integration lane

Production quality is proved by USE, not by green gates. Required:

- The increment's behavior is exercised through the REAL public surface (CLI,
  API, service, import of the shipped artifact) on the integration lane, at the
  merged SHA — artifact captured.
- `verification/loop` completed at that SHA (gates are the floor; real use is the
  ceiling).

Formal promotion to `main`/production stays operator-gated (`governance/rules`
§Stop). Integration-lane running is the enforceable bar; `main` promotion is a
separate, explicitly approved act. Never claim `main` promotion as sprint proof.

## Exit report

Per increment: SHA, gates, residue table with the command + result for each row,
**net LOC for the cycle**, real-surface artifact, Beads closed, PRs merged,
worktrees removed. Any non-empty residue row = increment NOT closed. Fix
in-sprint or STOP and surface it — never carry over silently.

## Context budget

Load: `UNIVERSAL_CORE` + this skill + `verification/loop` at closure time.
Skip: worker/orchestrator playbooks unless you also hold that role.
