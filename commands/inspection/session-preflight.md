---
name: session-preflight
description: "Run the read-only multi-agent preflight sweep before implementing in a shared fleet."
argument-hint: "[repository path]"
metadata:
  aihub.tags: '["decision:ADR-0028","route:agent"]'
---

# Session preflight

Read-only sweep before writing any code in a fleet workspace. It exists
because every measured failure of 2026-09-27 started with a session that
skipped it: discovering concurrent work by collision, closing beads in shared
trackers, building on stale lanes, re-implementing landed work.

1. Read the coordination thread first: `gc mail inbox` from a direnv-enabled
   repository; peek every message younger than your session. Your task may have
   been reassigned, blocked, or completed by another session while you were
   reading the plan.
2. Claim the bead and post your identity triple to the thread: bead id, branch,
   PR (or "PR to follow"). A session without a declared triple is invisible to
   the coordinator and duplicates someone.
3. Inventory the worktrees of your repository: `git worktree list`, last-commit
   age per worktree, dirty counts. A worktree idle for over an hour is
   abandoned — adopt it (fix-forward, adopt its staged work) or flag it to the
   coordinator; never delete another session's active lane.
4. Check open PRs sharing your files: `gh pr list --state open` plus
   `gh pr view <n> --json files`. A PR touching your files is a collision
   candidate — coordinate in-thread before implementing.
5. Check the integration branch state: fresh `git fetch`, ahead/behind of your
   lane, and the CI runs on the integration branch. A red integration branch
   freezes new feature work; the recovery is the P0.
6. Only after all five: implement in a dedicated worktree on a branch from the
   freshly fetched integration tip, with the bead claimed and the hourly
   progress cadence running.
