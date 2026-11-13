---
name: session-startup
description: Run the startup checklist before the first edit of the session.
metadata:
  aihub.tags: '["decision:ADR-0021","effective:2026-09-27","route:project"]'
---

# Session startup

Run this checklist in order before the first edit of the session.

1. **Handoff.** If a handoff was pointed at you, open it with `plan-handoff`:
   a handoff is one plan directory whose `00-index.md` indexes the landing
   records, ADRs, and beads; follow them before anything else.
2. **Governance.** Read `rules/law.md` and the surviving rules your work touches,
   starting with `rules/coordination/inter-session-mail.md`.
3. **Tracker.** `bd ready` and your claims: nothing you are about to do may
   duplicate an open bead. Adopt abandoned work under that rule instead of
   re-creating it.
4. **Prior art.** Search branches (local + remote), open PRs, and recent docs
   for the scope you were given. Found a survivor? Adopt it — the mandate is
   the outcome, not the authorship.
5. **Placement and ownership.** Placement follows `rules/git/gitflow-branch-pr.md`;
   overlapping WIP is kept (`rules/law.md` item 11).
6. **Declare the triple.** In a selected tracker workflow, claim the bead and record
   the actual branch and PR state there and in the coordination channel before the
   first effect (`rules/coordination/inter-session-mail.md`). A declaration grants no
   branch creation or Git publication authority.
7. **Cycle declared.** State which integration branch, which gates, and what
   runtime proof closes the unit (`rules/law.md` item 10).
