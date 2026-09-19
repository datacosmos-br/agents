---
description:
  One discovery frontier and one retirement executor for worktrees — the project wip
  program plans, the resident executor retires, Gas City places
capsule_summary: |
  Universal law (operator mandate 2026-09-19): a dedicated worktree exists to be
  discovered, measured, and — when its grain ends — retired. That lifecycle has exactly
  one discovery/planning frontier and exactly one executor per project.

  Discovery and planning belong to the project's declared wip program (its
  capture/plan/retire surface in the doc-10 vocabulary). Retirement's resident executor
  consumes the SAME candidate queue the wip planner produces; a second surface planning
  retirement over the same worktrees with a different policy is a defect. Placement and
  provisioning stay with Gas City; ad-hoc `git worktree` remains drift. Orphan/husk
  worktrees are in the project discovery's scope; rig runtime worktrees and foreign
  same-origin clones are excluded unless an explicit flag includes them.
metadata:
  aihub.tags: '["decision:ADR-0023","effective:2026-09-19","route:both"]'
---

# Worktree discovery and maintenance frontier

A dedicated worktree exists to be discovered, measured, and — when its grain ends —
retired. That lifecycle has exactly one discovery/planning frontier and exactly one
executor per project. A second policy over the same worktrees is the defect this rule
forbids.

1. **Discovery and planning belong to the project's wip program.** The project's
   declared wip surface — its capture/plan/retire program in the doc-10 vocabulary, for
   example a project's `wip` program — is the single owner that names the candidate set,
   its read-only correlation to beads, pull requests and actors, and the retirement
   intent. This catalog NAMES that owner class; it never reimplements discovery nor
   invents a parallel policy.
2. **Retirement has one executor.** The resident executor consumes the SAME candidate
   queue the wip planner produces. Two surfaces planning retirement over the same
   worktrees with different policies — for example merge-state versus an activity
   window — are forbidden: they double-retire or diverge.
3. **Placement is not discovery.** Provisioning and placement stay with Gas City
   (`coordination/gascity.md`); ad-hoc `git worktree` remains drift. Discovery reads the
   project's own registration and measurement surfaces, never a hand-maintained list.
4. **Scope.** Orphan/husk worktrees with no registration entry are inside the project
   discovery's scope. Rig runtime worktrees (Gas City runtime state) and foreign
   same-origin clones are excluded unless an explicit flag includes them.
