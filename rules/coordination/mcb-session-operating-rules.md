---
description: mcb lane discipline — integrated-or-lost cycles, bead freshness, evidence
  over exit codes
capsule_summary: |
  Operator rulings 2026-09-24..27 for agent sessions on marlonsc/mcb: work outside
  an integrated PR is lost work; a bead untouched for over one hour (claimed,
  deferred, or blocked included) is abandoned; "--force" is pre-authorized to
  unlock beads; an exit code without its log is not evidence; local make gates are
  the only CI (GitHub CI is off). Full context: docs/developer/AGENT-OPERATIONS.md
  in the repo and ADR 059 there for advisory triage.
metadata:
  aihub.tags: '["decision:ADR-0021", "effective:2026-09-27", "route:both"]'
---

# mcb session operating rules

For sessions working `marlonsc/mcb` (internal_flext rig). These rules specialize the
fleet-wide `full landing cycle or nothing` (rule file) and `beads verification` (rule
file) laws for that repository's gates and failure modes.

## Integration law

- Land in small cycles: lane, gates, PR, no-ff merge to `develop`, bead closed with
  evidence, lane retired. Minutes between green gates and merge, not hours; the
  integration branch tip is the only delivered state.
- Every lane is a dedicated `git worktree` with a physical `.venv` from `make setup`
  and `direnv allow` — never a symlinked venv, never the primary checkout.
- Before assuming a bead, search for pre-existing work: open PRs, remote branches,
  and upstream WIP branches. Adopt abandoned work; never redo or duplicate work
  another session is actively driving (prove recency before touching it).

## Beads law

- A bead untouched for more than one hour is abandoned — claimed, deferred, and
  blocked included. Assumed beads get a lane-note comment at claim time.
- Housekeeping is part of the job: dedupe, close superseded, realign epics, fix
  titles. `--force` is operator-authorized to unlock beads; record why in the bead.
- Closure requires evidence in the bead: merge commit, captured gate results, or
  structural proof. "Done" without a command output is a lie.

## Verification law

- Local make gates are the only CI. Run each isolated with its exit code captured:
  `make gen check`, `CI=Y make check`, `CI=N make check`, `make test`,
  `make rust WHAT=test`.
- An exit code is not evidence. Read the log (`test result:`, the assertion) before
  declaring red or green; a compile failure is not a test failure, and a
  zero-execution result is red, never passed.
- Root cause only: no bypass, no shim, no retry, no catch normalization, no silent
  filtering. A warning beats silence; a fix beats both.

## Coordination law

- Report bead, branch, and PR to the coordinator by mail at claim time and at
  landing time.
- Critique other sessions with evidence, never blame without it; stop and ask the
  operator when two rules collide or authority is missing.
