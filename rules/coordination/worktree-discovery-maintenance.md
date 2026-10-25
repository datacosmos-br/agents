---
description:
  One discovery frontier for worktrees and native retirement at landing — the project
  wip program plans and reports, the landing lane retires itself, the activation
  boundary owns placement
capsule_summary: |
  Discovery and planning of existing worktrees belong to the project's declared wip
  program. Discovery does not provision isolation or make a checkout disposable.

  Retirement applies to invocation-owned disposable lanes: retire eligible worktrees
  and branches with Git after the merge, only once ownership and
  `git merge-base --is-ancestor <ref> origin/<integration>` exits 0 against a freshly
  fetched base. A merged, patch-equivalent, or projection-only lane is retired the same
  way after its evidence is recorded. Never retire an adopted primary/shared checkout
  or integration branch. Placement follows gascity, not a fresh-lane prerequisite.
  Orphan/husk worktrees are in the project discovery's scope; rig runtime worktrees and
  foreign same-origin clones are excluded unless an explicit flag includes them.
metadata:
  aihub.tags: '["decision:ADR-0027","effective:2026-09-24","route:personal"]'
---

# Worktree discovery and maintenance frontier

Discovery has one frontier per project. Existing worktrees are measured without
requiring new isolation. Eligible disposable lanes retire through their native owner;
adoption of an existing context does not authorize its deletion.

1. **Discovery and planning belong to the project's wip program.** The project's
   declared wip surface is the single owner that names the candidate set, its read-only
   correlation to beads, pull requests and actors, and the retirement intent. This
   catalog NAMES that owner class; it never reimplements discovery nor invents a
   parallel policy.
2. **Retirement is native and scoped.** An invocation-owned disposable lane retires
   in the same cycle when authorized: fetch the integration base, prove
   `git merge-base --is-ancestor <ref> origin/<integration>`, then delete the remote
   branch, remove the worktree, and delete the local branch with Git. A lane whose
   commits are merged, patch-equivalent, or projection-only is retired the same way
   after its evidence (tip SHA, diffstat, patch of any uncommitted state) is recorded
   on the tracker. An absent executor, planner, or verb never defers retirement:
   accumulated worktrees are the defect this rule exists to prevent.
3. **Placement is not discovery.** Provisioning and placement follow
   `rules/coordination/gascity.md`: active Gas City orchestration uses its transactional
   owner when selected, and manual execution follows that same canonical rule's
   current-authorization boundary. Discovery reads the project's own
   registration and measurement surfaces, never a hand-maintained list.
4. **Scope.** Orphan/husk worktrees with no registration entry are inside the project
   discovery's scope. Rig runtime worktrees (Gas City runtime state) and foreign
   same-origin clones are excluded unless an explicit flag includes them.

These retirement steps apply only to an existing lane whose removal is authorized.
The Git preservation owner still requires complete tracked, index and untracked-content
preservation, current integration proof and absence of active ownership. An ancestry
check alone does not authorize deletion, and a shared checkout is not disposable
because one task ends.
