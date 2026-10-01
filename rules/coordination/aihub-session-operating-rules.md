---
description: Acting rules for any agent session working the ai-hub fleet, earned across the 2026-09 runtime campaigns.
metadata:
  aihub.tags: '["decision:ADR-0030","effective:2026-09-27","route:personal"]'
---

# ai-hub session operating rules

Acting rules for any agent session working ai-hub (distilled from the
operator's directives across the 2026-09 runtime campaigns; each rule earned
the hard way — the campaign retrospective lives in
ai-hub `.kilo/plans/2026-09-27-surfaced-inventory-runtime-recovery/00-index.md`).

## Integration law

- One mandate per lane. Lane → gates green → commit (≈15 min cadence: the
  commit is the context checkpoint) → `merge --no-ff` with the tip →
  fast-forward push → close the bead with evidence → retire the lane.
- The primary checkout may be another session's lane. Never merge, generate, or
  install from it; land through a dedicated merge worktree
  (`worktree add -b temp/land origin/dev` + `merge --no-ff <lane>` + push the
  merge tip fast-forward) and retire the merge worktree.
- Validate before pushing; a silly red on the PR is the defect, not the CI's.
- Never edit or run inside a worktree another agent is actively driving. Adopt
  its valid published commits immediately by cherry-pick into your own lane
  cut from the fresh tip (rule `lane ownership declaration`); never wait for it
  to land and never adopt a workaround commit.

## Beads law

- A bead untouched for more than 1 hour is abandoned — claimed, deferred, and
  blocked included.
- Closing requires command evidence: merge commit, captured gate output, or
  structural proof written into the bead. "Done" without a command output is a
  lie. Notes carry pointers (ADRs, cursor plans, handoffs), never the whole
  record.

## Coordination law

- Report bead/branch/PR to the coordinator when starting work and when landing
  it; delivery proven, not assumed.
- Critique other sessions' violations with evidence, never blame without it.

## Verification law

- An exit code is not evidence: read the log (the test result line, the
  assertion) before declaring RED or GREEN.
- Zero-execution results, warnings, and skips are RED. Generated artifacts
  (`source-receipt.json` and siblings) must exist before a battery is honest —
  run the repository's generator verb in a fresh worktree first.
- Attribute before re-running: group failures by file and reason, run one
  representative per group, cure each at its owner, then re-run the full
  battery.

## Environment law

- Inherited unit markers (`INVOCATION_ID`, `SYSTEMD_EXEC_PID`,
  `GC_SUPERVISOR_*`) say nothing about the current process; context comes from
  the cgroup leaf (ADR-0030). Unsetting a marker to pass a guard is a bypass —
  cure the guard.
- A worktree's environment is physical and exclusive (`make setup`, own
  `.venv`); never borrow, symlink, or place it under `/tmp`.
- Read the domain model's validators before writing fixtures or tests — the
  typed model is the specification (uniqueness, ordering, and map-shape
  contracts live there).

## Stop-and-ask triggers

Contract conflicts, authority boundaries (operator-only mutations), and any
case where two rules collide: present both rules with references and ask.
