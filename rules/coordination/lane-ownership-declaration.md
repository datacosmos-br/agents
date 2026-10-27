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
   authorized lane — never rebuilt unnecessarily. Workaround
  commits are rejected with the reason recorded, never adopted. Editing or
   running in an unselected checkout grants no authority; a shared checkout
   explicitly selected by the operator remains usable with coordinated WIP.
   Deleting an active lane is prohibited.
metadata:
  aihub.tags: '["decision:ADR-0021","effective:2026-10-01","route:both"]'
---

# Lane ownership declaration and the abandonment clock

## Declare before the first commit

A lane is declared with three identifiers, sent to the coordinator through the
mail channel and written on the canonical bead:

- **bead** — claimed (`--claim`) with the scope comment;
- **branch** — the current authorized branch and checkout, selected through
  `rules/coordination/gascity.md`, with its relationship to the current integration tip;
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

1. Resolve the authorized checkout and branch through the placement owner and
   inspect the current integration tip; do not create a new lane by implication.
2. Cherry-pick the valid published commits you need, by SHA (`git
   cherry-pick -x <sha>`), into that lane. Adoption happens through commit
   objects when that Git action is authorized. Shared-checkout collaboration follows
   current operator authorization and `fix-forward-collaboration`; do not switch
   another actor's branch or overwrite its WIP.
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

- Preserve every actor's live contributions. Coordinate overlapping owners without
  treating their presence as a ban on an operator-authorized shared checkout.
- Criticism of another session's violations goes through the coordinator mail
  channel, with the rule numbers, never through their files.
- Critical doubt goes to the coordinator; the coordinator escalates to the
  human operator.
