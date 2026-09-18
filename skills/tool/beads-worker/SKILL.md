---
name: beads-worker
description: "beads execution, scoped work, tracker workflow"
metadata:
  aihub.tags: '["activation:opt-in","decision:ADR-0008","detect:opt-in:beads-worker","effective:2026-08-29","route:agent","subject:beads","usage:router"]'
---

# Beads Worker

Activate only for a currently assigned implementation slice. Semantic graph changes,
reassignment, merge, and issue closure remain owner operations.

Before editing, verify from current evidence the issue identity and revision,
assignment, unblocked dependencies, exact file scope, existing checkout and branch,
acceptance contract, integration target, and required gates. A foreign, stale,
ambiguous, or blocked assignment stops before effects.

For managed shared work, verify the city-store root and child linked by the local bead.
Record repository evidence locally and cross-rig dependency, handoff, producer SHA, and
integration state in the shared child. Reread both at each material checkpoint;
disagreement stops effects for owner reconciliation.

Execute only the assigned slice through repository owners. Preserve concurrent work,
eliminate superseded code and rewired-consumer residue, and propagate the first command
or gate failure unchanged. Correct an in-scope owner and rerun the invalidated native
path; do not repeat unchanged, switch execution paths, normalize red evidence, or
perform a tracker mutation. Owner-only work remains active in the same issue and is
handed to that owner, never treated as closure.

Resolve Available versus Explicitly suspended from the active repository contract.
During suspension, do not invoke or replace Beads and create no substitute tracker or
ledger. Preserve evidence only in separately authorized Git, PR, review, check, and CI
surfaces. Handoff must state issue, branch, SHA, scoped files, exact
command/exit/decisive output, PR and integration evidence, residue, and unverified
owner-only work. Report ready for review only when the slice itself is validated and
residue-free; never infer merge or closure.

## Evidence and update discipline

- Work starts only after the bead is claimed; every repo-state change (commit, regen,
  relock, submodule pointer, gate result) is written back to the bead as a note before
  the next change begins.
- Evidence is runtime, not attestation: paste command, working directory, exit status,
  and decisive output. "Should pass" or "logic is correct" is not evidence.
- Generated projections are never hand-edited; change the owner input, rerun the
  generator twice to a fixed point, and record both runs.
- On resume, reconcile bead notes against live `git status`/`git log` first; the
  worktree is fresher than the note and wins.

## Tracker Discipline

- Claim before effects: `bd update <id> --claim` precedes the first file write or
  mutating command; update the bead after every repository-state change.
- `--json` output from `bd` commands is a list, not an object; parse accordingly.
- Close only with proof: the closure reason starts with `DONE:`, `SUPERSEDED:`, or
  `OBSOLETE:` and names the exact command, exit code, decisive output, and commit SHA.
- Work discovered inside the slice becomes a new bead linked with `discovered-from`;
  never absorb it silently into the assigned slice.

## Execution discipline (fleet slices, 2026-09-10)

- Dispatcher acceptance proof: `make <verb>` (help), `WHAT=<action> make <verb>` (must
  reach the real script; downstream credential failures belong to the action, not the
  dispatcher), `make help` listing the verbs.
- On FF push rejection: `git merge --no-ff` the integration tip into your lane,
  revalidate, repush; never rebase or force-push.
