---
description:
  Declare bead + branch + PR before any effect; keep every touched bead alive
  inside the configured abandonment threshold; re-check open PRs and the integration tip before opening
  a lane; adopt abandoned work instead of redoing it.
capsule_summary: |
  Operator ruling 2026-09-27: work performed outside an integrated lane is
  work totally lost. A lane exists only when its bead (claimed), its branch,
  and its PR are declared to the coordinator before the first commit, and
  every touched bead is updated within the configured abandonment threshold —
  claimed, deferred, and blocked included. Before opening a lane, re-check open PRs, the
  integration tip, and abandoned branches: adopt their work (fix forward),
  never rebuild it. Tracker memory operator-ruling-2026-10-01-adopt-by-cherry-pick:
  an active lane is adopted
  immediately by cherry-picking its valid published commits into your own
  lane cut from the fresh tip — never awaited, never asked about. Workaround
  commits are rejected with the reason recorded, never adopted. Editing or
  running inside another session's worktree is a violation; deleting an
  active lane is worse.
metadata:
  aihub.tags: '["decision:ADR-0021","effective:2026-10-01","route:both"]'
---

# Lane ownership declaration and the abandonment clock

## Declare before the first commit

A lane is declared with three identifiers, sent to the coordinator through the
mail channel and written on the canonical bead:

- **bead** — claimed (`--claim`) with the scope comment;
- **branch** — cut from the freshly fetched integration tip in a dedicated
  worktree on the destination filesystem;
- **PR** — the receiving integration branch, named in the declaration even
  before the PR exists.

Work without this declaration is unowned. Unowned work is lost work.

## The abandonment clock

The abandonment test and its configured threshold are declared once, in
[bead-branch-pr-cadence](bead-branch-pr-cadence.md) §2. Keep every touched bead alive
with a progress comment at each boundary (effect applied, gate passed, PR
opened, merge landed). A bead you let go stale is a bead another session will
assume or duplicate.

## Re-check before you build (R9 made operational)

Before opening any lane: fetch the integration branch, list open PRs, and
check the activity of the remote branch that would carry your work. Sessions
in this fleet land in bursts; a lane built against a stale tip duplicates
work that is already landing.

## Adopt active lanes by cherry-pick, immediately

When another session's lane — active or abandoned — carries work your target
needs, adopt it now (tracker memory
`operator-ruling-2026-10-01-adopt-by-cherry-pick`). Waiting for it to land, asking
permission to adopt, or parking your own lane behind it is a violation.

1. Cut your own lane from the freshly fetched integration tip.
2. Cherry-pick the valid published commits you need, by SHA (`git
   cherry-pick -x <sha>`), into that lane. Adoption happens through commit
   objects only: never edit files, run commands, or check out branches inside
   the other session's worktree.
3. Adopt only root-cause work. A commit that carries a workaround — timeout or
   budget inflation, suppression, catch-based normalization, fallback, retry,
   shim — is rejected, never cherry-picked; record the rejected SHA and the
   reason on the owning bead and PR, and cure the defect at its owner in your
   lane.
4. Post a `[coord]` note on the source PR and bead naming the adopted and the
   rejected SHAs, as standard procedure, not as a request.

## Adopt abandoned work

Branches, PRs, worktrees, and beads abandoned under
[bead-branch-pr-cadence](bead-branch-pr-cadence.md) §2 are inputs, not
obstacles: diff them against the integration tip, port what is still useful
into your lane, and record the disposition of the rest. Never rebuild
from scratch what an abandoned branch already carries; never discard what you
did not read.

## Boundaries

- The primary checkout carrying another session's live work is hands-off —
  even when it looks like churn you would have restored.
- Criticism of another session's violations goes through the coordinator mail
  channel, with the rule numbers, never through their files.
- Critical doubt goes to the coordinator; the coordinator escalates to the
  human operator.
