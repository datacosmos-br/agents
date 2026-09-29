---
description:
  Declare bead + branch + PR before any effect; keep every touched bead alive
  on a one-hour clock; re-check open PRs and the integration tip before opening
  a lane; adopt abandoned work instead of redoing it.
capsule_summary: |
  Operator ruling 2026-09-27: work performed outside an integrated lane is
  work totally lost. A lane exists only when its bead (claimed), its branch,
  and its PR are declared to the coordinator before the first commit, and
  every touched bead is updated at least once per hour — claimed, deferred,
  and blocked included. Before opening a lane, re-check open PRs, the
  integration tip, and abandoned branches: adopt their work (fix forward),
  never rebuild it. Colliding with an active lane is a violation; deleting an
  active lane is worse.
metadata:
  aihub.tags: '["decision:ADR-0021","effective:2026-09-27","route:both"]'
---

# Lane ownership declaration and the one-hour clock

## Declare before the first commit

A lane is declared with three identifiers, sent to the coordinator through the
mail channel and written on the canonical bead:

- **bead** — claimed (`--claim`) with the scope comment;
- **branch** — cut from the freshly fetched integration tip in a dedicated
  worktree on the destination filesystem;
- **PR** — the receiving integration branch, named in the declaration even
  before the PR exists.

Work without this declaration is unowned. Unowned work is lost work.

## The one-hour clock

A bead with more than one hour without an update is abandoned — this applies
to claimed, deferred, and blocked beads alike. Keep every touched bead alive
with a progress comment at each boundary (effect applied, gate passed, PR
opened, merge landed). A bead you let go stale is a bead another session will
assume or duplicate.

## Re-check before you build (R9 made operational)

Before opening any lane: fetch the integration branch, list open PRs, and
check the activity of the remote branch that would carry your work. Sessions
in this fleet land in bursts; a lane built against a stale tip duplicates
work that is already landing. If another session is actively working your
target, adopt their output when it lands instead of racing it.

## Adopt abandoned work

Branches, PRs, worktrees, and beads with no activity beyond the abandonment
threshold are inputs, not obstacles: diff them against the integration tip,
port what is still useful into your lane, close with recorded disposition
what is superseded, and delete the residue with ancestry proof. Never rebuild
from scratch what an abandoned branch already carries; never discard what you
did not read.

## Boundaries

- The primary checkout carrying another session's live work is hands-off —
  even when it looks like churn you would have restored.
- Criticism of another session's violations goes through the coordinator mail
  channel, with the rule numbers, never through their files.
- Critical doubt goes to the coordinator; the coordinator escalates to the
  human operator.
