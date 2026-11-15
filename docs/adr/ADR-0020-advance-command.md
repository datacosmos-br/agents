# ADR-0020 — Advance: one command for evidence-based phase transitions

**Status:** Accepted **Date:** 2026-09-10 **Scope:**
`commands/implementation/advance.md`, `docs/research/agent-instruction-design.md`,
`config/governance.json`

## Context

Resuming interrupted plans required re-pasting a long operator prompt each session; the
prompt mixed universal law with one-session task lists and inlined skill content, so it
aged badly and duplicated its owners. Research (see
`docs/research/agent-instruction-design.md`) shows persistence phrasing, state
restoration from evidence, verbal reflection, executable verification, and progressive
disclosure through skills are the mechanisms that make an agent resume and drive a plan
to verified completion.

## Decision

1. `advance` owns the work order and the phase readiness decision. It repairs the active
   phase and starts the next authorized phase only when `sprint-closure` can establish
   closure on the integrated revision. Missing proof blocks the transition and leaves
   independent work actionable. `$ARGUMENTS` locates the plan, bead, or project.
2. Stack deltas (Python, FLEXT, others) stay in their branch-matched law skills; the
   command routes to owners and duplicates nothing — parallel per-stack command variants
   are rejected.
3. The research dossier is evidence referenced by guarantee
   `instruction-design-evidence`; it is never an authority and never
   proposal-presented-as-current-architecture.

## Consequences

- Session resumption becomes one deterministic entry point instead of a re-authored
  prompt; the capsule budget is untouched (the command loads on demand).
- Future law changes flow into the routed skills and rules, not into command bodies.
