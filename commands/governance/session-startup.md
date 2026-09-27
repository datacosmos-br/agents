---
description: Session startup checklist — become competent before touching code
capsule_summary: |
  Operator ruling 2026-09-27, after a session that started blind (governance
  unread, prior art unsearched, coordinator uninformed) and lost work for it.
  Run this at session start, before the first edit.
metadata:
  aihub.tags: '["decision:ADR-0021","effective:2026-09-27","route:both"]'
---

# Session startup

Run this checklist in order, before the first edit of the session. Each step
existed as a rule before; this is the one-place sequence.

1. **Handoff index.** If a handoff document was pointed at you
   (`~/.claude/plans/handoff-*`), read it — it is an index; follow its
   references to the landing records, ADRs, and beads before anything else.
2. **Governance.** Read `~/agents/rules/coordination/` headers relevant to
   your work: `full-landing-cycle`, `bead-branch-pr-cadence`,
   `lane-ownership-declaration`, `inter-session-mail`, `operator-precedence`.
3. **Tracker.** `bd ready` and your claims: nothing you are about to do may
   duplicate an open bead. Adopt abandoned work (>1h silent) instead of
   re-creating it.
4. **Prior art.** Search branches (local + remote), open PRs, and recent docs
   for the scope you were given. Found a survivor? Adopt it — the mandate is
   the outcome, not the authorship.
5. **Lane ownership.** Identify the primary checkout's owner session; hands
   off. Your lane is a dedicated worktree on the destination filesystem.
6. **Declare the triple.** Claim the bead, create the branch, and announce
   bead + branch + PR to the coordinator via `gc mail human` — before the
   first commit, not after the first scolding.
7. **Cycle declared.** State which integration branch, which gates, and what
   runtime proof closes the unit (full-landing-cycle step 1).
