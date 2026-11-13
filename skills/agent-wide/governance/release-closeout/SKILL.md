---
name: release-closeout
description:
  "integration closeout, push-sync audit, superproject merge, lane commits, tracker
  evidence"
license: MIT
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-09-10","usage:router"]'
  version: 1.1.0
---

# Release Closeout

Activate before landing an integration branch: superproject gitlink commits,
projection-only commits, and any closeout audit that lands member work into the
workspace.

## Member push-sync audit before gitlink commits

Before committing a subproject (gitlink) pointer in the superproject, check every
touched member: the gitlink moves only when `git -C <member> rev-parse HEAD @{push}`
prints one SHA twice. A missing, diverged or unreachable `@{push}` would point the
gitlink at work no lane or CI can see: push the member, or stop and report the blocker.

## Projection-only commits under concurrent WIP

When other lanes hold WIP in the same member, commit projection-only files (regenerated
facets, rendered templates, generated docs) with explicit paths — never `git add -A` or
`git add .`. Staging by explicit path keeps another lane's in-flight source edits out of
the projection commit. If the projection commit cannot be made without sweeping unknown
WIP, stop and coordinate instead of committing.

## Regeneration note

Generated file headers read `@flext-regenerate: make gen` with no apply acknowledgement:
every verb runs directly, with no apply selector or mutation guard.

## Superproject PR merge playbook (release lane → integration branch)

- Concurrent WIP is kept (`rules/law.md` item 11). Closeout needs no new merge
  worktree and grants no checkout change or publication from analysis.
- Conflict classes: (1) submodule/gitlink → OURS when integration tips are newer and
  pushed; (2) generated facade `__init__.py` → THEIRS when theirs is the more complete
  public facade; (3) prohibited lock/pin artifacts → remove from the merged result and
  repair their producer in the same change. Never select OURS or THEIRS for a banned
  artifact.
- Everything else: decide per file, prefer fix-forward (preserve the other lane's
  legitimate work), and record every resolution.
- Commit with an explicit merge message listing the resolution classes on the release
  lane and validate that SHA with `make gen` (fixed-point gate) before pushing it; the
  integration branch receives it only through the reviewed PR
  (`rules/git/gitflow-branch-pr.md`), never a direct push.

## Concurrent-lane protocol (git index contention)

- A sibling lane running `flext_infra codegen conform` loops creates transient
  `.git/index.lock`; never delete a live lock, never kill the other lane's processes.
- Coordinate and serialize index mutations with the current owner; retry only within
  the agreed bounded window. Contention does not select another worktree.
- Commit by explicit paths only: gitlinks + stable projections first; leave files a
  sibling lane is actively rewriting (for example the typed dependency config or
  generated `pyproject.toml`) to that lane, then verify and adopt after their push. A
  banned lock/pin file is never preserved as concurrent WIP; fix the producer and remove
  the artifact.

## Beads evidence contract during closeout

- Per resolved blocker, one evidence comment: command, exit code, decisive output line
  and pushed SHA range.
- New discovered work becomes a task bead with
  `--deps discovered-from:<integration-bead>`.
- Never close the integration bead until: all members push-synced (audit above),
  superproject gitlinks committed+pushed, PR merge landed, and gen fixed-point green on
  the merged tip.

## Runner environment gates (CI closeout)

- GitHub runners check out files as 0664 (umask 002), which exact-mode gates reject; the
  CI workflow template normalizes modes once after checkout, before any gate, and the
  canonical verification is never weakened.
- A remote gate failure is reproduced locally under the runner's umask before it is
  fixed; only a failure matching the CI log proves the cause, and a clone under the
  developer's own umask proves nothing about the runner.
