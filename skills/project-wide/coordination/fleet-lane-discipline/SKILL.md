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
