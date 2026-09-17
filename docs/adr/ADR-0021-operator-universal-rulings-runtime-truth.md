# ADR-0021 — Operator universal rulings of 2026-09-15/16: runtime truth, no rushed work, full landing cycle

**Status:** Accepted
**Date:** 2026-09-16
**Scope:** `rules/coordination/validate-on-change.md`, `rules/coordination/wip-persistence.md`, `rules/coordination/full-landing-cycle.md`, `rules/coordination/never-deduce.md`, `rules/coordination/green-green-landing.md`, `rules/coordination/lane-adoption.md`, `rules/coordination/fanout-qa-publication.md`, `rules/ethics/test-reality-law.md`, `rules/ethics/strict-typed-quality.md`, `rules/ethics/conformance-sweep.md`

## Context

The operator issued four universal rulings during the 2026-09-15/16 fleet
stabilization sessions, after repeated cycles where green tests and collected
evidence coexisted with broken runtime behavior, and where work parked outside
a dedicated lane (or short of the integration branch) was lost:

1. Creating or changing anything is validated by full functioning in real
   runtime — simple tests and evidence artifacts are never the fundamental
   proof.
2. No work is rushed to conclusion: status and beads update continuously, and
   WIP is committed and pushed locally and remotely through the dedicated
   worktree and working branch.
3. A unit of work that never reaches the integration branch — and, when
   requested, the deployed runtime — is not done at all: the full landing
   cycle is what converts work into delivered work.
4. Never deduce or guess: research the owner, understand, and when doubt
   remains, stop and ask one precise question before mutation proceeds.

## Decision

1. Each ruling is encoded as one canonical rule under `rules/coordination/`
   (`validate-on-change`, `wip-persistence`, `full-landing-cycle`,
   `never-deduce`) and their
   companion rules produced by the same sweep (`green-green-landing`,
   `lane-adoption`, `fanout-qa-publication`, `test-reality-law`,
   `strict-typed-quality`, `conformance-sweep`), all approved by this ADR.
2. The rules are universal (route both): they bind every execution context —
   agent sessions, rigs, and every hosted project — unless a stack's own law
   is stricter.
3. Runtime functioning is the acceptance authority for every change; tests and
   gates are bookkeeping around that judgment, never a substitute for it.

## Consequences

- Every session starts and continues under these rules without re-declaring
  them; governance projections regenerate from the canonical rule files.
- Work reporting must distinguish "landed on the integration branch (and
  running in runtime when in scope)" from "in progress with the exact missing
  step" — partial cycles are never reported as done.
