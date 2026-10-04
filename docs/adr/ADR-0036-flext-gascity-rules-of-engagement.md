# ADR-0036 — Flext × Gas City rules of engagement: one fleet, two governing layers

- **Status:** Accepted
- **Date:** 2026-10-04
- **Tracking:** operator-approved harmonization plan 2026-10-04; rule
  `rules/coordination/flext-gascity-roe.md`

## Context

The fleet's Python architecture law (flext: facades `c/t/p/m/u` + operational
letters, one `api.py` MRO per package, declaration-only Pydantic 2 models, DI,
config SSOT, the green gate ladder) and the Gas City orchestration law (cities,
rigs, lanes, dispatch, Beads evidence, closure) evolved in separate documents.
Agents working a lane read both, but no durable rule binds them together: the
campaign discipline measured during fleet stabilization (CONTROL §9.1/§9.8 —
serialized `make` actor, agent cutoff, admin-merge timing, post-merge probe)
lived only in a session control journal, and the universal core existed in three
drifting copies. An agent reading only one side either refuses an authorized
admin-merge or skips the green obligation after it.

## Decision

1. **One fleet, two layers, one precedence.** Flext law governs how Python code
   is written in any lane of any repository; Gas City law governs orchestration
   (cities, rigs, lanes, dispatch, Beads, closure). Precedence stays: operator
   order > city `AGENTS.md` > rig `AGENTS.md` > Beads > governance bundle.
2. **Core composition, no fourth copy.** The AIHUB prelude is the shared base;
   flext's UNIVERSAL-GOVERNANCE core is the flext-domain delta consumed in the
   `rules/flext/session-router.md` order. Drift between cores is fixed at the
   owning source and re-projected — never reconciled by hand-copying.
3. **Green is never waived, only timed.** Admin-merge before CI green changes
   when green is measured, not whether: gates re-run on the merged SHA, the
   runtime proof executes, and the import/publication probe validates before
   any closure claim.
4. **Campaign discipline is durable law.** During a campaign all fleet
   `make`/gate work flows through one serialized actor (per-rig Dolt contention
   killed two agents on 2026-10-03); Bead writes stay sequential and
   coordinator-only; an agent counts as active only with a gc-mail message on or
   after the current campaign cutoff (2026-10-02 at declaration).
5. **Language boundary is explicit.** Go repositories (gascity, beads) follow
   their own `AGENTS.md`/`TESTING.md`; only the process law is shared across
   languages. The zero-violation code gate keeps its single declaration in
   `rules/workflow/canonical-commands.md`; the flext `smells` gate is an
   additional structural gate in flext-family repositories, not the spelling
   gate.

## Consequences

`rules/coordination/flext-gascity-roe.md` is the reference agents load for
harmonization questions; CONTROL.md §9 refinements that match this ADR are now
restatements and drift there is corrected toward this rule. City-level prompt
injection references the rule through a template fragment instead of copying
it. Simplification work cites the flext doctrine owners
(`rules/architecture/engineering-core.md`,
`rules/flext/generator-declarations.md`); no rule invents numbers or verbs.
