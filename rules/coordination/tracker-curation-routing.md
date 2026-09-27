---
description: Tracker curation routing — one owner per tracker, evidence per close, shared-tracker closes route through the coordinator
metadata:
  aihub.tags: '["decision:ADR-0028","effective:2026-09-27","route:agent"]'
---

# Tracker curation routing

When two sessions curate the same bead tracker, every close is duplicated work
or lost work. Each tracker has exactly one curation owner at a time; a session
that finds a bead to close in a tracker it does not own posts the id and its
evidence in the coordination thread instead of closing it.

# Curation rules

1. Claim before curate: a curation batch starts by claiming its umbrella bead
   and posting the batch scope (which beads, which law applied).
2. One decisive check per close: a close carries file:line proof (feature/fix
   live in the source), a measurement (the failure no longer reproduces), or a
   successor pointer (the work moved to another bead).
3. Shared trackers route through the coordinator: post id + evidence in-thread;
   the coordinator cross-checks and applies. Never close directly.
4. Staleness law: a bead untouched for more than one hour — in any state,
   including claimed, deferred or blocked — is abandoned; the next session
   claims it or hands it back. Progress notes reset the clock.
5. Disposition before deletion: worktrees and branches are removed only after
   an inventory proves their content is absorbed (zero unique commits vs the
   integration line) or the unique content is exported and recorded.
6. Real backlog survives: a bead whose demand is not yet implemented stays open
   with refreshed evidence (measured counts, current file:line of the gap) —
   staleness alone never closes a genuine demand.
