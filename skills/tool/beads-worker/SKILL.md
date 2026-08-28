---
name: beads-worker
description: 'Execute one Beads-scoped lane when tracker work is explicitly authorized.'
bundle: beads
scope: universal
metadata:
  aihub.tags: '["activation:opt-in","detect:opt-in:beads-worker","provenance:agents-owned","route:agent","tool:beads","updates:manual","usage:router"]'
---

# Beads Worker

## Authority

See `UNIVERSAL_CORE`; `governance/rules` §Execution / §Continuous-Green / §Evidence. Not restated here.

## Before Claiming

1. Only beads assigned or handed by orch. `bd show`: read NOTES; continue from evidence.
2. Skip blocked (`bd blocked`); verify moved-DB blockers.
3. One bead, one path scope in the **shared** epic/feature worktree (never per-agent worktree).

## During

- SHORT ATOMIC CYCLES: one bounded outcome; commit + push + Bead evidence; validator PASS before orch integrates.
- ZERO-RED: never commit/push/handoff with lint/type errors in scope — fix in-cycle.
- COOPERATIVE FIX-FORWARD: adopt concurrent useful hunks; never clobber or revert other lanes.
- Evidence: `bd update <id> --append-notes "<date> <slice>: cmd=… cwd=… exit=… decisive=… not-verified=…"`
- File discovered work immediately (`-t discovered-from`). Living docs in the same change.

## Conflict Escalation

Re-parented/blocked/foreign claim → stop, re-read, confirm with orch. Overlapping PRs → serialize via orch. Duplicates → link; orch dedupes. Unresolvable → one precise question with both states.

## Closure Path

Report `READY_FOR_REVIEW`, `NEEDS_FIX`, or `BLOCKED` with branch, SHA, diffstat, gates, real-use, PR/CI, risks. Push + PR. Merge/close/rollout = orch only.

Leave ZERO residue for your Bead: superseded code deleted, all consumers and tests rewired, no shim. A Bead whose increment cannot close because of your slice is NOT `READY_FOR_REVIEW`. See `verification/closure`.

## Context Budget

Load: UNIVERSAL_CORE + governance/rules + this skill + project AGENTS (+ provider domain law when marker active).
