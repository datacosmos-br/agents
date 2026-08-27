# Conflict Catalog And Convergence Protocol

Observed in live opencode sessions (2026-07-20, dual-orchestrator day).
Goal: every conflict converges to one coordinated truth — never force.

## Detection First

Before every mutation batch, re-read the slice you are about to change
(`bd show`, `bd list --json`). If the graph changed since your audit (new
closes, deps, assignees, re-parents), STOP and re-audit. Never blind-reapply
a stale plan — concurrent owners are a normal condition, not an anomaly.

## Conflict Classes

1. **Claim collision** — bead assigned to another agent. Do not touch. If you
   need it, ask the operator/orchestrator for explicit reassignment; record
   the handoff in notes. Never self-reassign a live claim.
2. **Dual orchestrators** — two agents doing semantic mutations on one
   tracker. Exactly one orchestrator per tracker scope, designated by the
   operator. The other stands down to read-only audit or takes a disjoint
   scope (different repo/DB). While parallel is unavoidable: restrict
   yourself to non-overlapping mutation classes and re-verify after each
   batch. Claim concentration (one agent holding ~100% of the board) is a
   risk to report, not a license to grab lanes.
3. **Zombie lanes** — `in_progress` with no live worker; teams from dead
   sessions still listed active. Orchestrator reclaims: `status open` + note
   with abandonment evidence. If the owner might still be live, ask the
   operator one precise question instead.
4. **Dirty shared checkout** — WIP from another lane in the integration
   checkout. Never implement there. Classify hunks before touching anything
   (fix-forward law: unknown = preserve). Work in your own worktree; if
   target files are dirty from another lane, sequence via the orchestrator.
5. **Stale tracker state** — blocked-by-closed, status/dependency mismatch,
   NULL epic descriptions. These are audit findings: fix per
   `consolidation.md` §Hygiene; never freeze on them.
6. **Mirror divergence** — GitHub vs Beads drift. Correct immediately toward
   Beads (the SSOT); never maintain two truths or bespoke sync glue.
7. **Premature "done"** — claims require command + cwd + exit + decisive
   output + bounded scope. If the operator asks "did you actually finish?",
   the answer is evidence or "no" — never a rephrased maybe. Compaction,
   status reports, and self-reports complete nothing (UNIVERSAL_CORE 10, 12).
8. **Rule-stack conflicts** — duplicate governance injections or
   contradictory guidance. Newest explicit operator instruction wins;
   reconcile lower authorities; report the duplication as an audit finding
   (it feeds over-injection cleanup), never stack rival rules silently.

## Escalation

Any conflict not resolvable by these rules = ONE precise question to the
operator, with evidence of both states. Forbidden resolution moves:
reassigning others' beads, reverting unknown hunks, closing others' work,
force-push, or inventing a parallel tracker.
