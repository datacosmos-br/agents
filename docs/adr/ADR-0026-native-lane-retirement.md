# ADR-0026 — Native lane retirement; the projection-landing law is removed

**Status:** Accepted **Date:** 2026-09-24

## Context

Two laws blocked lane retirement:

- **`rules/workflow/projection-landing-automation.md`** (`effective:2026-09-19`). It
  allowed a projected surface to reach a repository only through a "distributor's landing
  verb". It made opening a worktree, deleting a file, or opening a pull request by hand a
  process defect.
- **The single-retirement-executor clause** of
  [ADR-0023](ADR-0023-worktree-discovery-maintenance-frontier.md), carried by
  `rules/coordination/worktree-discovery-maintenance.md`. It required a resident executor
  consuming the wip planner's candidate queue.

Neither the landing verb (`ai-hub workspace-landing`) nor the resident executor, nor the
`ai-hub wip <verb>` program that ADR-0023 names, exists in the AI Hub CLI. Measured on
2026-09-24: the CLI exposes only the `wip-hier` planner, and its `--apply` merely aligns
branches.

With both laws in force, no lane was ever retired. Measured on 2026-09-24:

- ai-hub had 28 registered worktrees;
- the FLEXT fleet had about 140 worktrees and about 400 extra remote branches across its
  32 repositories;
- most were already merged into their integration branch.

The operator ordered the landing law removed on 2026-09-24, and on the same day approved
amending the single-executor clause, stating that the accumulation of junk worktrees came
from these laws.

## Decision

1. `rules/workflow/projection-landing-automation.md` is deleted. A projection's writable
   authority and regeneration contract stay with `rules/workflow/generators-not-projections.md`.
   The landing cycle stays with `rules/git/gitflow-branch-pr.md`.
2. Retirement is native and immediate. Clause 2 of
   `rules/coordination/worktree-discovery-maintenance.md` now reads:
   - the lane that landed retires its own worktree and local and remote branches with
     Git in the same cycle;
   - it does so after `git merge-base --is-ancestor <ref> origin/<integration>` exits 0
     against a freshly fetched base;
   - a merged, patch-equivalent, or projection-only lane is retired the same way, after
     its evidence is recorded on the tracker.
3. An absent executor, planner, or verb never defers retirement. Discovery and planning
   remain with the project's wip program (ADR-0023, decision 1). Placement remains as
   recorded in [ADR-0025](ADR-0025-manual-worktrees-during-orchestration-suspension.md).
4. This decision supersedes ADR-0023 decision 2 and its 2026-09-19 amendment items on
   the resident executor. ADR-0023 decisions 1, 3, and 4 are unchanged.
5. **Lanes outside the session's own worktree.**
   - `rules/shell/bash-guard-lane-execution.md` stated that Claude Code worktree
     isolation refuses `git -C <path>` and `env -C <path> make <verb>` outside the
     session's worktree. Measured on 2026-09-24, both forms run normally. The premise
     was false, and the rule made fleet-wide landing and retirement impossible from one
     coordinating session.
   - The operator ruled on 2026-09-24 that a lane in another checkout or repository is
     reached with `git -C <lane> <verb>` and `env -C <lane> make <verb>`.
   - `cd` into another checkout and `make -C` remain prohibited.

## Consequences

- The accumulated merged lanes across the fleet are retired with Git, lane by lane, each
  with an ancestry proof and recorded evidence. No new verb is a precondition.
- A lane that is not merged is adjudicated by its authored content before retirement.
  Projection-only diffs are not a contribution unless the operator overrides a specific
  item.
- AI Hub regenerates the home projection of the rules, which removes the deleted rule from
  every provider home on the next publication.
