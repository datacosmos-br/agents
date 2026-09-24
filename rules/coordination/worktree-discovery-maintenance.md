---
description:
  One discovery frontier for worktrees and native retirement at landing — the project
  wip program plans and reports, the landing lane retires itself, the activation
  boundary owns placement
capsule_summary: |
  Universal law (operator mandate 2026-09-19, retirement amended 2026-09-24): a
  dedicated worktree exists to be discovered, measured, and — when its grain ends —
  retired. Discovery and planning belong to the project's declared wip program.

  Retirement is native and immediate: the lane that landed retires its own worktree and
  local and remote branches with git right after the merge, once
  `git merge-base --is-ancestor <ref> origin/<integration>` exits 0 against a freshly
  fetched base. A merged, patch-equivalent, or projection-only lane is retired the same
  way after its evidence is recorded. Retirement never waits for an executor that does
  not exist. Placement and provisioning follow the Gas City activation boundary: active
  orchestration uses its owner; manual execution uses dedicated native Git worktrees.
  Orphan/husk worktrees are in the project discovery's scope; rig runtime worktrees and
  foreign same-origin clones are excluded unless an explicit flag includes them.
metadata:
  aihub.tags: '["decision:ADR-0026","effective:2026-09-24","route:personal"]'
---

# Worktree discovery and maintenance frontier

A dedicated worktree exists to be discovered, measured, and — when its grain ends —
retired. Discovery has exactly one frontier per project; retirement is a native Git
step of the landing cycle, never a deferred job.

1. **Discovery and planning belong to the project's wip program.** The project's
   declared wip surface is the single owner that names the candidate set, its read-only
   correlation to beads, pull requests and actors, and the retirement intent. This
   catalog NAMES that owner class; it never reimplements discovery nor invents a
   parallel policy.
2. **Retirement is native and immediate.** The lane that landed retires itself in the
   same cycle: fetch the integration base, prove
   `git merge-base --is-ancestor <ref> origin/<integration>`, then delete the remote
   branch, remove the worktree, and delete the local branch with Git. A lane whose
   commits are merged, patch-equivalent, or projection-only is retired the same way
   after its evidence (tip SHA, diffstat, patch of any uncommitted state) is recorded
   on the tracker. An absent executor, planner, or verb never defers retirement:
   accumulated worktrees are the defect this rule exists to prevent.
3. **Placement is not discovery.** Provisioning and placement follow
   `rules/coordination/gascity.md`: active Gas City orchestration uses its transactional
   owner; manual execution uses a dedicated native Git worktree, branch, and physical
   environment on the authorized destination filesystem. Suspension never authorizes
   implementation in the primary/default checkout. Discovery reads the project's own
   registration and measurement surfaces, never a hand-maintained list.
4. **Scope.** Orphan/husk worktrees with no registration entry are inside the project
   discovery's scope. Rig runtime worktrees (Gas City runtime state) and foreign
   same-origin clones are excluded unless an explicit flag includes them.
