---
description: Adopt the current worktree and never discard it with Git
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-08-29","route:both"]'
---

# Adopt the current worktree and never discard it with Git

Two `git reset` runs wiped multi-agent worktrees and endangered shared state.
Treat every current change in an authorized repository or worktree as owned input,
regardless of when it appeared or who authored it. These are forbidden as change
management operations:

`git reset`, `git checkout -- .`, `git restore`, `git clean -xdf`/`-Xdf`,
`git stash`, `git rebase`, `git revert`, `git push --force`.

- Stage only reviewed, intentional paths (`git add <scoped paths>`); never
  `git add -A`/`.` at a workspace or umbrella root.
- Never stage a directory that may contain a linked worktree. Git records a
  directory carrying its own `.git` as a gitlink (mode `160000`) the moment it is
  staged, silently and with no `.gitmodules` entry. Git then cannot resolve a URL
  for it, so `git submodule update --init` exits 128 and every consumer fetching
  that repository as a dependency fails during checkout, before reading a line of
  its code. Nothing local reports it. Stage files, and when gathering changed
  paths for a WIP-preservation commit take them from `git status --porcelain`
  rather than from a directory.
  Two integration branches were made unfetchable this way — flext-infra, where
  `make setup` went red for every consumer in the fleet, and the workspace
  umbrella, where a second instance sat unnoticed. Which command staged them is
  not established: the WIP-preservation script already skips any path holding a
  `.git`, so some other add did it. That is exactly why the invariant is written
  as a prohibition on the act rather than as a fix to one tool. Detection is
  owned by the `index-declarations` gate in flext-infra, which fails the build on
  any gitlink the repository does not declare — after the commit exists. This
  clause is what keeps it from existing.
- Apply `rules/coordination/fix-forward-collaboration.md`; recover evidence from
  `git reflog` only when authorized, never by replacing the adopted current state.
- Commit often so the combined work survives a lane or process failure.

See also: `operator-precedence.md` (rule file) — integration authority.
