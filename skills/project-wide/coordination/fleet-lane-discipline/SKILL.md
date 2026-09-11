---
name: fleet-lane-discipline
description: 'submodule ownership, lane recovery, ci projection, fix-forward landing'
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-09-10","usage:router"]'
  version: 1.0.0
---

# Fleet Lane Discipline

Use when coordinating lanes across a superproject and submodule trees.

- Assign exactly one active owner per tree, including each submodule checkout.
  Never run two lanes in the same checkout.
- When a lane is stalled for more than 30 minutes by last-write mtime, resume the
  existing `task_id`. Supply the ready decision, current evidence, next command,
  and acceptance condition; never create a duplicate tree owner.
- CI workspace validation follows gitlinks: gate every submodule projection
  before changing its root pointer. Land submodules first, then update pointers
  in a separate root commit.
- Keep lane logs in the canonical durable location. Never use `/tmp` for lane
  logs or recovery evidence.
- Use absolute fix-forward: preserve and adopt the current authorized worktree,
  integrate with `git merge --no-ff`, and revalidate the combined tree. Rebase,
  force-push, cherry-pick replacement, and branch rewriting are prohibited.
- Open PRs early so CI can run in parallel while gates close. An early PR is a
  coordination surface, not merge authorization.

## Conformance sweep over superprojects

Apply when executing cleanup/conformance sweeps on hosted projects with
submodule fleets and parallel actors.

- The tracker store is per-project: when touching another project's tracker,
  unset the provider-database session override for the command family. Never
  inherit or guess a database; verify the resolved store first.
- Roll up superproject gitlinks in a dedicated root commit after the submodule
  merge is on its declared integration branch; re-fetch the remote and prove
  `git merge-base --is-ancestor <sha> origin/<base>` before any deletion the
  rollup justifies.
- Retire a lane in the same cycle it lands: ancestor-proof against a
  just-fetched base, then remove the worktree, delete the local branch, the
  remote branch, and prune stale tracking refs. Empty `git worktree list` is
  the acceptance evidence.
- Prove zero residue (`*.bak`, `*.tmp`, generated backups) through the
  generator itself — a green `make gen` fixed point — never through a manual
  `find` after failed or partial runs, and never through literal-grep
  heuristics (a literal environment probe cannot prove a grouped-Make
  variable test).
- Never enter active reform territory of another actor (locked epic, live
  lane). Document the boundary, claim only non-overlapping classes, and absorb
  their landed work after merge instead of re-solving it.
- Ping the fleet before claiming a shared theme (message/mail surface) and
  re-absorb the integration tip at every material step; late discovery of a
  moving tip costs one full lane cycle per miss.
- Close a bead only with evidence scoped to the exact gate state at closure:
  a partially failing pipeline is never cited as green; name which part is
  green and file the failing remainder as its own bead.
- When landing under admin merge with checks still pending, rerun the affected
  gates on the merged SHA before the next wave, and record which gates were
  rerun. Pending-CI merges are an authorized exception, never a silent norm.
- Bulk edits over many files need a declared owner (Make verb or generator),
  per-file review intent, and downstream gates rerun; blanket textual
  replacement over prose without reading each diff is a residue generator.
- A new governance index entry (skill, rule, command) requires a
  capsule-budget ADR when the delivery contract reports the budget
  near-exhausted; wording updates to an existing body do not.
