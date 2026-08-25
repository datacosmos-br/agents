---
name: crew-commit
description: "Canonical Gas Town commit workflow for crew members. USE FOR: committing lane work with agent identity (gt commit), branch hygiene, staging discipline, opening PRs into the merge queue. DO NOT USE FOR: dispatching work (gt sling); tracker semantics (beads-orchestrator); merging (Refinery only)."
license: MIT
metadata:
  bundle: github
  scope: universal
---

# Crew Commit

Flow: preflight → branch → stage → commit → push → PR. Never commit `main`; the Refinery owns merges.

## Workflow

1. **Preflight**: `git fetch origin`; confirm branch ≠ `main`. Behind → rebase; conflict you cannot resolve cleanly → STOP, escalate.
2. **Branch**: `<type>/<short-desc>` (`feat/ fix/ refactor/ docs/ chore/ test/`) or `crew/<name>/<desc>`.
3. **Stage**: specific paths, never blind `git add -A`. Verify diff: no `.env`, secrets, debug code, unrelated hunks. Watch submodule pointers (`git submodule status`) — stage pointer bumps only with intent.
4. **Commit**: `gt commit -m "<type>: <what and why>"` — sets agent identity from `GT_ROLE`. Imperative mood, subject ≤50 chars.
5. **Push**: `git push -u origin <branch>`.
6. **PR**: `gh pr create` with summary + test plan. Work lands via merge queue (`gt done` on the bead; Refinery verifies and merges).
7. **Notify** (optional): `notify "PR ready: <desc> #<n>"`.

## Critical rules

- `gt commit`, never raw `git commit` (identity comes from role).
- Force-push forbidden; resolve root cause or escalate.
- Committed to main by mistake → stop immediately, call operator.
