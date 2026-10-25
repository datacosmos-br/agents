# ADR-0021 — Operator universal rulings of 2026-09-15/16: runtime truth, no rushed work, full landing cycle

**Status:** Accepted; placement attribution corrected 2026-10-23
**Date:** 2026-09-16 **Scope:**
`rules/coordination/validate-on-change.md`, `rules/coordination/wip-persistence.md`,
`rules/coordination/full-landing-cycle.md`, `rules/coordination/never-deduce.md`,
`rules/coordination/green-green-landing.md`, `rules/coordination/lane-adoption.md`,
`rules/coordination/parallel-delegation.md`, `rules/ethics/test-reality-law.md`,
`rules/ethics/strict-typed-quality.md`, `rules/ethics/conformance-sweep.md`

## Context

The dedicated-worktree wording in this historical context is not current law or
verified universal operator authority. The 2026-10-23 amendment below supersedes
that placement attribution without rewriting the historical record.

The operator issued four universal rulings during the 2026-09-15/16 fleet stabilization
sessions, after repeated cycles where green tests and collected evidence coexisted with
broken runtime behavior, and where work lacking durable preservation or integration
was lost:

1. Creating or changing anything is validated by full functioning in real runtime —
   simple tests and evidence artifacts are never the fundamental proof.
2. No work is rushed to conclusion: status and beads update continuously, and WIP is
   preserved through the repository's authorized checkpoint and integration workflow.
3. A unit of work that never reaches the integration branch — and, when requested, the
   deployed runtime — is not done at all: the full landing cycle is what converts work
   into delivered work.
4. Never deduce or guess: research the owner, understand, and when doubt remains, stop
   and ask one precise question before mutation proceeds.

## Decision

1. Each ruling is encoded as one canonical rule under `rules/coordination/`
   (`validate-on-change`, `wip-persistence`, `full-landing-cycle`, `never-deduce`).
   Companion rules produced by the same sweep (`green-green-landing`, `lane-adoption`,
   `parallel-delegation`, `test-reality-law`, `strict-typed-quality`,
   `conformance-sweep`) may add only a narrow, non-overlapping delta and must reference
   the canonical owner instead of copying its contract. All are approved by this ADR.
2. The rules are universal (route both): they bind every execution context — agent
   sessions, rigs, and every hosted project — unless a stack's own law is stricter.
3. Runtime functioning is the acceptance authority for every change; tests and gates are
   bookkeeping around that judgment, never a substitute for it.

### Placement amendment - 2026-10-23

The operator's correction at 21:56:04 UTC (ag-wibx.2) retires universal isolation
prerequisites. ADR-0025 owns adoption of the current checkout and optional placement
by invocation type. Persistence does not require another worktree or branch, nor
make an adopted workspace disposable. Other runtime and integration requirements
remain with their owners.

## Consequences

- Every session starts and continues under these rules without re-declaring them;
  governance projections regenerate from the canonical rule files.
- Work reporting must distinguish "landed on the integration branch (and running in
  runtime when in scope)" from "in progress with the exact missing step" — partial
  cycles are never reported as done.

## Governance consolidation — 2026-10-20

The duplicate fan-out rule is retired into `parallel-delegation`. Current
operator and role authorization determine inline versus delegated execution;
the historical maximum-fan-out mandate does not launch agents for every task.
The execution owner retains sequenced acceptance and publication.

## Placement attribution correction — 2026-10-23

The current operator explicitly rejects a mandatory new worktree, branch and
environment for every manual task. The historical placement claim above cannot
be used to impose it or prohibit the primary checkout. Follow the single
placement owner, [`gascity`](../../rules/coordination/gascity.md), and the
attribution correction in
[ADR-0025](ADR-0025-manual-worktrees-during-orchestration-suspension.md).
Runtime truth, WIP preservation and authorized integration remain mandatory;
none grants deletion, isolation or Git publication authority by implication.
