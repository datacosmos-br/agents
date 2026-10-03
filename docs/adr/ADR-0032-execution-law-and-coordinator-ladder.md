# ADR-0032 — Execution-law router skill and the coordinator ladder

- **Status:** Accepted
- **Date:** 2026-10-01
- **Tracking:** `ag-f2u1` (governance alignment campaign, agents rig)

## Context

Sole-executor engagements — the operator's recurring "total monopoly, execute to
completion" directives (2026-09-24 through 2026-10-01) — are governed piecewise:
`rules/runtime/strict-execution.md`, `rules/coordination/lane-adoption.md`,
`rules/coordination/full-landing-cycle.md`, the `make-check` and
`verification-loop` skills, and `sprint-closure`. No single artifact composes
them for a cleanup, finalization, or quality campaign, so each session
reconstructs the contract and drops pieces of it.

Coordination has the inverse gap. When the Gas City mayor or supervisor tier is
down (measured 2026-10-01: supervisor active, mayor and every dispatcher
suspended), no rule resolves who coordinates. Sessions default to ad-hoc
assumptions, and the operator's ladder directive — active mayor first;
otherwise an election through the mail channel; otherwise degraded solo with
reconciliation — lives only in conversation.

## Decision

1. **One router skill composes the owners.** `execution-law`
   (`skills/agent-wide/governance/execution-law/`, path-owned agent-wide
   routing, `usage:router`) activates for sole-executor plan execution,
   cleanup, and finalization engagements. It is a delta-only router: it
   declares no new conduct, composes the existing owners in one fixed order,
   and carries the engagement contract in `references/procedure.md`.

2. **The coordinator ladder is a rule.**
   `rules/coordination/coordinator-ladder.md` (`route:personal`) resolves the
   coordinator from live evidence, never assumption: an active mayor or
   supervisor coordinator is the only Tier-1 authority; otherwise an election
   through the mail channel decides one agent by self-nomination with a
   deterministic tie-break; otherwise the session proceeds as a degraded solo
   coordinator, recording coordination decisions on its bead and reconciling
   through the human channel when it returns.

3. **The election window is the configured abandonment threshold.** The
   ladder introduces no numeric tunable: a nomination unanswered past
   `coordination.abandonment_threshold_minutes`
   (`config/governance.json`, declared by ADR-lineage of PR #199) leaves the
   assuming session the default coordinator. The general cure for tunables
   hardcoded in governance artifacts remains owned by `ag-qcsj`.

4. **No bootstrap membership.** The skill stays out of
   `config/governance.json` bootstrap lists; the capsule budget gate
   (ADR-0019) is untouched, and sessions reach the skill through home
   projection and the restore list.

5. **Project deltas extend, never fork.** A project domain (for example the
   FLEXT provider) may publish a skill carrying `extends:execution-law`; the
   catalog copy stays project-neutral and the scope gate keeps host-command
   vocabulary out of project-projected records.

## Consequences

- A cleanup or finalization session composes one named owner instead of
  rediscovering the piecewise law, and the plan-level contract (startup
  census, adoption before rewrite, extermination, gated configuration,
  native-gate evidence, full landing, zero-residue closure) has a citable
  home.
- Coordinator resolution is deterministic and single-holder: silent-window
  default assumption plus hand-back only through a recorded handoff prevents
  two coordinators, and an election never stalls execution.
- Homes-only routing keeps the ladder's `gc`/`bd` command vocabulary out of
  project projections.

## Verification

- `make audit`, `make check`, and `make waza` validate the inventory; the
  suite under `evals/execution-law/` grades the three canonical roles.
- The ADR index bijection and every relative docs link resolve under
  `make docs`.
