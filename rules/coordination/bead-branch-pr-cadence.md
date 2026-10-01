---
description: Acting cadence — bead identity, dedupe mandate, the configured abandonment threshold, and the CI=Y emission canon
capsule_summary: |
  Operator rulings 2026-09-27. Every work unit is declared as bead + branch + PR
  to the coordinator at claim time; a bead (any state), lane, worktree, branch,
  or PR without change for the configured abandonment threshold is ABANDONED
  and may be adopted by anyone (adoption never authorizes deletion); before
  starting any unit, research whether the work already exists in
  abandoned branches, open PRs, or other beads — redoing existing work or two
  actors doing the same thing is a severe violation; the dedupe of the tracker
  (close superseded, realign epics, fix titles, --force when the tracker refuses) is part
  of the acting role, not an extra.
metadata:
  aihub.tags: '["decision:ADR-0021","effective:2026-10-01","route:both"]'
---

# Bead + branch + PR cadence and the dedupe mandate (operator ruling 2026-09-27)

Composes with [full-landing-cycle](full-landing-cycle.md) (the cycle is what
delivers) and [fleet-landing-corrections](fleet-landing-corrections.md).

## 1. Identity at claim time

1. Every work unit carries its triple from the moment work starts: the claimed
   **bead**, the dedicated **branch**, and the **PR** (opened as soon as the
   commit exists, updated as work lands).
2. The coordinator is informed of the triple through the coordinator mail channel
   at claim time and at every material state change (land, blocker, scope change).
3. The branch is dedicated (one mandate per lane, ruling 58): `fix/<slug>-<date>`
   from the current integration tip, in a dedicated worktree on the destination
   filesystem — never `/tmp`, never a borrowed venv, never the primary checkout.

## 2. Abandonment after the configured threshold without change

This section is the single owner of the abandonment test (operator ruling
2026-10-01). Its threshold is a tunable value, declared only in the governance
config key `coordination.abandonment_threshold_minutes` and validated whenever the
bundle loads. Any consumer reads it through the published package as
`GovernanceBundle.load().config.coordination.abandonment_threshold_minutes`. No rule,
skill, command, or doc restates the number; each references this section.

1. A bead in any state (claimed, deferred, blocked), a lane, a worktree, a branch,
   or a PR is abandoned once the threshold passes without a change. A change is
   the newest of: the bead's recorded update, the branch's last commit or push,
   the PR's last update, and the last file modification in its worktree. Anyone
   may adopt it; adoption is a choice, never an obligation.
2. Adopting means claiming the bead, announcing `[coord] lane claim`, and
   continuing the existing work with `merge --no-ff` (or by cherry-picking
   isolated commits) into the adopter's lane. It never means rewriting work that
   already exists.
3. Abandonment authorizes adoption, never destruction or closure. Retiring a
   branch or worktree follows `gitflow-branch-pr` (rule file) and the city
   reaper's backup precondition; closing a bead follows
   [beads-canonical-epics](beads-canonical-epics.md).
4. Heartbeats record the measured state on the bead as an appended note, not
   "still working". Adoption supersedes re-creation: pick the bead up, record the
   adoption, continue from its notes.
5. Epics and parents are kept alive the same way; a stale `updated_at` with a
   same-day comment is cured by a heartbeat, not by opening a duplicate.

## 3. Dedupe mandate (part of the acting role)

1. Before starting any unit: search branches (local and remote), open PRs, and
   open beads for the same scope. Adopt the survivor; never re-implement.
2. Superseded work closes `SUPERSEDED` naming the survivor (three legal closure
   reasons only, per [beads-canonical-epics](beads-canonical-epics.md)).
3. Duplicates found in flight are retired after containment proof
   (`git diff` against the survivor shows no unique content).
4. Tracker hygiene is continuous: close what is already done, realign beads to
   the correct epic, fix misleading titles, and use `--force` when the tracker's
   state machine refuses a lawful operation.

## 4. Validate locally, land in short cycles

1. The local gate runs BEFORE the PR exists: `CI=Y make gen` ×2, `make fix`,
   `make fmt`, `make check`, and the full suite — a silly red on CI is a
   violation, not bad luck.
2. The repository canon for generation is the CI runner's emission
   (`CI=Y make gen` on a fresh checkout). A local-context generation must never
   be swept into a commit: if the CI-context paths were dirtied, restore them
   from the origin tip before pushing.
3. Land in short cycles (commit + push early, PR immediately, merge on green) —
   unlanded work is lost work (ruling 2026-09-27, "full landing cycle"
   [full-landing-cycle](full-landing-cycle.md)).
