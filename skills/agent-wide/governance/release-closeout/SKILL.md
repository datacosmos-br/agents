---
name: release-closeout
description: 'integration closeout, push-sync audit, superproject merge, lane commits, tracker evidence'
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

Before committing a subproject (gitlink) pointer in the superproject, audit
every touched member's push state. Update the gitlink only when the member
HEAD is already pushed:

```sh
git -C <member> rev-parse HEAD @{push}
```

If `@{push}` is missing, diverged, or unreachable, the gitlink would reference
work no lane or CI can see. Push the member (or stop and report the blocker)
before landing the pointer. Never commit a gitlink to a member state that is
not push-synced.

## Projection-only commits under concurrent WIP

When other lanes hold WIP in the same member, commit projection-only files
(regenerated facets, rendered templates, generated docs) with explicit paths —
never `git add -A` or `git add .`. Staging by explicit path keeps another
lane's in-flight source edits out of the projection commit. If the projection
commit cannot be made without sweeping unknown WIP, stop and coordinate
instead of committing.

## Regeneration note policy (2026-09-10)

Generated file headers read `@flext-regenerate: make gen` — without `APPLY=Y`.
`make gen` is provisioning/idempotent-safe with its own fixed-point verify, so
the regeneration note must not require the mutation guard. The corrected guard
pattern is `ifneq ($(filter-out Y Y,$(strip $(APPLY))),)` — `$(filter-out PATTERN,TEXT)`: pattern first, text second. An inverted argument
order makes the guard always error. Mutation verbs other than `gen` still
require `APPLY=Y`; never weaken their guards.

## Superproject PR merge playbook (release lane → integration branch)

- Execute the merge in a dedicated worktree
  (`git worktree add <path> -b merge/<pr>-<from>-to-<to> <integration-branch>`),
  never in a live checkout; never push from the analysis phase.
- Conflict classes: (1) submodule/gitlink → OURS when integration tips are
  newer and pushed; (2) generated facade `__init__.py` → THEIRS when theirs
  is the more complete public facade; (3) `uv.lock` → OURS (authoritative, newer).
- Everything else: decide per file, prefer fix-forward (preserve the other
  lane's legitimate work), and record every resolution.
- Commit with an explicit merge message listing the resolution classes;
  validate the merged SHA with `make gen` (fixed-point gate) BEFORE
  pushing.
- Pushing the merge commit to the integration branch auto-merges the GitHub
  PR — no `gh merge` needed.

## Concurrent-lane protocol (git index contention)

- A sibling lane running `flext_infra codegen conform` loops creates transient
  `.git/index.lock`; never delete a live lock, never kill the other lane's
  processes.
- Retry the commit in a bounded loop (e.g. 40 attempts, 15s sleep) — the
  commit window between conform iterations is enough.
- Commit by explicit paths only: gitlinks + stable projections first; leave
  files a sibling lane is actively rewriting (e.g. `pyproject.toml`/`uv.lock`
  during a deps upgrade) to that lane, then verify and adopt after their push.

## Beads evidence contract during closeout

- Per resolved blocker, one evidence comment: command, exit code, decisive
  output line, pushed SHA range (e.g. `make setup` → EXIT=0, "Resolved
  281 packages"; push `382b06ec5..39abee778`).
- New discovered work becomes a task bead with
  `--deps discovered-from:<integration-bead>` (e.g. floor-writer
  ceiling-awareness from the fleet-integration bead).
- Never close the integration bead until: all members push-synced (audit
  above), superproject gitlinks committed+pushed, PR merge landed, and gen
  fixed-point green on the merged tip.

## Runner environment gates (CI closeout)

- GitHub runners expose umask 002: `git checkout` materializes tracked
  non-executable files as 0664, and exact-mode canonical gates (e.g. Mise
  artifact spec 0o644) fail loud on the drift. The CI workflow template owns
  the fix: normalize once after Checkout (`chmod -R go-w .`) before any gate;
  never weaken the canonical verification.
- Reproduce a remote gate failure locally before fixing: clone with the
  simulated runner umask (`umask 0002` → observed 0664) or apply the minimal
  drift (`chmod 664`) and run the canonical verb; a failure that byte-matches
  the CI log proves the root cause and validates the fix. A fresh clone under
  the developer's own umask (022) proves nothing about runner behavior.
