---
name: mcb-cycle
description:
  "Run one full marlonsc/mcb work cycle for a bead — lane, battery, PR, no-ff merge,
  bead closure, lane retirement."
argument-hint: "<bead-id> [branch-slug] [--match nextest-filter]"
metadata:
  aihub.tags: '["decision:ADR-0021","effective:2026-09-27","route:project"]'
---

# mcb cycle

Treat `$ARGUMENTS` as the bead id, an optional branch slug, and an optional nextest
match filter. Load the repository's `docs/developer/AGENT-OPERATIONS.md` runbook and
follow it exactly; the command only sequences the cycle.

1. **Startup**: pull the integration branch with drift restored; search open PRs and
   remote branches for pre-existing work on the bead; claim the bead with a
   lane-note comment; mail the coordinator the bead, branch, and (later) PR.
2. **Lane**: dedicated `git worktree` at `/home/marlonsc/mcb-wt-<slug>`, branch off
   `origin/develop`, `make setup` for a physical `.venv`, `direnv allow`.
3. **Battery**: `make gen check`, `CI=Y make check`, `CI=N make check`, `make test`,
   `make rust WHAT=test` (add `MATCH=$ARGUMENTS` filter when given). Each gate
   isolated, exit code captured; read the logs, never trust a bare rc.
4. **Landing**: push, `gh pr create --base develop` with the proof table in the body,
   merge with a merge commit, post-merge proof on the integration branch.
5. **Closure**: close the bead with the full evidence trail, retire the lane
   (worktree remove, branch -D), mail the coordinator the landing.
