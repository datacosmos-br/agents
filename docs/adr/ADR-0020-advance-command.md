# ADR-0020 — Advance: one resumption-and-force-advance command owned by skill routing

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

1. One command, `advance`, owns resumption plus forced advancement: Phase 0 authority,
   Phase 1 evidence-based state restoration, Phase 2 reflection checkpoint, Phase 3
   advance loop with per-step skill routing, Phase 4 executable verification, Phase 5
   landing and closure, and a final restatement of non-negotiables (recency effect).
   `$ARGUMENTS` carries the optional focus; session tasks are never hardcoded into the
   body.
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
