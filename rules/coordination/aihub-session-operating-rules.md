---
description: Acting rules for any agent session working the ai-hub fleet, earned across the 2026-09 runtime campaigns.
metadata:
  aihub.tags: '["decision:ADR-0030","effective:2026-09-27","route:personal"]'
---

# ai-hub session operating rules

These procedures apply to the selected ai-hub context. Campaign retrospectives
are evidence, not universal placement authorization; current placement follows
`rules/coordination/gascity.md`.

## Integration law

- One mandate follows the current Git owner's complete reviewed integration cycle,
  native acceptance and required runtime proof. Retire only an explicitly authorized,
  invocation-owned disposable lane after that owner's preservation and fresh ancestry
  proof; never retire an adopted primary/shared/integration context by task closure.
- Resolve the actual authorized checkout and branch through the placement owner;
  do not invent a primary-checkout ban or a separate merge-worktree prerequisite.
- Validate before pushing; a silly red on the PR is the defect, not the CI's.
- Coordinate overlapping owners and adopt compatible work under
  `fix-forward-collaboration`; concurrent edits do not invalidate shared-checkout
  authorization. Never overwrite unknown WIP or adopt a workaround commit.

## Beads law

- Bead abandonment follows `bead-branch-pr-cadence` (rule file) §2.
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
   run the repository's generator verb in the authorized checkout first.
- Attribute before re-running: group failures by file and reason, run one
  representative per group, cure each at its owner, then re-run the full
  battery.

## Environment law

- Inherited unit markers (`INVOCATION_ID`, `SYSTEMD_EXEC_PID`,
  `GC_SUPERVISOR_*`) say nothing about the current process; context comes from
  the cgroup leaf (ADR-0030). Unsetting a marker to pass a guard is a bypass —
  cure the guard.
- `shared-venv-guard` owns the physical environment at the actual runtime root;
  a new task or gate does not imply a new environment.
- Read the domain model's validators before writing fixtures or tests — the
  typed model is the specification (uniqueness, ordering, and map-shape
  contracts live there).

## Stop-and-ask triggers

Contract conflicts, authority boundaries (operator-only mutations), and any
case where two rules collide: present both rules with references and ask.
