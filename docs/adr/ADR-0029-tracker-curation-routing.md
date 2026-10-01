# ADR-0029 — Tracker curation routing: one owner per tracker, evidence per close, shared-tracker closes route through the coordinator

**Status:** Proposed **Date:** 2026-09-27 **Scope:** rules/coordination/tracker-curation-routing.md

## Context

On 2026-09-27 the ai-hub/flext/gascity campaign ran four concurrent sessions
across three bead trackers. Measured failures from that day:

- Two sessions closed beads in the flext tracker: the coordinator ruled one
  pair of closes invalid-by-routing (gc-wisp-18g6yk: "Two sessions closing the
  same tracker is exactly the duplication the operator condemned") and demanded
  the ids + evidence for verification or reopen.
- An orphan `~/.beads` dolt store grew through bd's `$HOME` walk-up fallback
  while sessions ran `bd` from non-repo directories; its databases carried
  auto-initialized schemas and one placeholder issue, and its removal required
  an inventory (issue export) plus a stop through bd's own verb before deletion
  was safe.
- Ten+ worktrees accumulated across gascity and ai-hub with no bead mapping
  several of them; at least one lane changed hands mid-work (created for a
  deploy attempt, adopted by the census session for ADR-0028) and the original
  creator discovered the adoption only by collision.

Root cause in all three: tracker curation had no declared owner per tracker,
and worktree disposition had no inventory-or-evidence gate.

## Decision

1. Every tracker declares exactly one curation owner at a time; the owner is
   recorded in the coordination thread. A session that is not the owner closes
   nothing: it posts the id and its evidence in-thread, and the owner
   cross-checks and applies.
2. Every close carries its proof: a file:line measurement that the demanded
   capability is live, a negative reproduction, or a successor pointer to the
   bead that now owns the work. Closes without proof are reopened.
3. A bead abandoned under the test of `rules/coordination/bead-branch-pr-cadence.md`
   §2 (amendment, operator ruling 2026-10-01: the threshold is a configured value
   declared only there) is claimed by the next session or handed back with a
   progress note. Progress notes reset the clock.
4. Worktrees and branches are removed only after an inventory proves their
   content is absorbed (zero unique commits against the integration line) or
   their unique content is exported and recorded; the inventory accompanies the
   disposition.
5. Genuine demands are never closed for staleness alone: a bead whose request
   is unimplemented stays open with refreshed evidence (current file:line of
   the gap, measured counts).

The rule text is `rules/coordination/tracker-curation-routing.md`.

## Consequences

- Sessions must check the coordination thread (gc mail) before curating a
  tracker and post ownership + batch scope before the first close.
- Duplicate curation of one tracker becomes a visible routing violation instead
  of silent lost work.
- Stale-but-real backlog survives with refreshed evidence; the tracker's open
  count measures real work again.
- The `$HOME/.beads` walk-up fallback (bd default) requires sessions to run bd
  from repository directories; the orphan-store inventory of 2026-09-27
  (six databases, five empty scaffolds, one exported placeholder) is the
  recorded precedent.

## References

- Measured instance: ai-hub bead `aihub-bxz9w` (proxy redeploy execution
  record), gascity beads `gct-x4dgu` (closed), `gct-tsq2z` (dedup batch
  evidence), `gct-3jyse` (open queue).
- Operator ruling thread: gc-wisp-18g6yk, gc-wisp-lnbzki, gc-wisp-p8slwv
  (2026-09-27).
