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
  never rebuild it. Adoption follows the current Git owner after refreshing the
  declared integration ref, not the historical cherry-pick mechanism. Workaround
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

## Adopt current work through the Git owner

When another session's lane — active or abandoned — carries work your target
needs, reconcile it promptly through `rules/git/gitflow-branch-pr.md`. The historical
2026-10-01 cherry-pick instruction does not override that owner's current merge,
preservation and publication contract.

1. Resolve the authorized checkout and branch through the placement owner and
   fetch the declared integration ref and retain its refspec/tip evidence before
   comparing contributions; do not create a new lane by implication.
2. Identify the valid published commits by SHA and adopt through the current Git
   owner, accounting for work already integrated in the fresh base. Shared-checkout collaboration follows
   current operator authorization and `fix-forward-collaboration`; do not switch
   another actor's branch or overwrite its WIP.
3. Adopt only root-cause work. A commit that carries a workaround — timeout or
   budget inflation, suppression, catch-based normalization, fallback, retry,
   shim — is rejected, never adopted; record the rejected SHA and the
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
