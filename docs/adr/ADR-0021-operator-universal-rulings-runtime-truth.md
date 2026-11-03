# ADR-0021 — Operator universal rulings of 2026-09-15/16: runtime truth, no rushed work, full landing cycle

**Status:** Superseded by ADR-0038
**Date:** 2026-09-16 **Scope:**
`rules/coordination/validate-on-change.md`, `rules/coordination/wip-persistence.md`,
`rules/coordination/full-landing-cycle.md`, `rules/coordination/never-deduce.md`,
`rules/coordination/green-green-landing.md`, `rules/coordination/lane-adoption.md`,
`rules/coordination/parallel-delegation.md`, `rules/ethics/test-reality-law.md`,
`rules/ethics/strict-typed-quality.md`, `rules/ethics/conformance-sweep.md`,
`rules/ethics/no-preexisting-debt.md`,
`rules/workflow/canonical-commands.md`, `rules/workflow/structural-migrations.md`,
`rules/workflow/mass-rewrite-discipline.md`, `rules/workflow/generators-not-projections.md`,
`rules/architecture/internal-clean-architecture.md`, `rules/architecture/rule-exceptions.md`

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
placement owner, [`gascity`](https://github.com/datacosmos-br/agents/blob/f9161bfb/rules/coordination/gascity.md), and the
attribution correction in
[ADR-0025](ADR-0025-manual-worktrees-during-orchestration-suspension.md).
Runtime truth, WIP preservation and authorized integration remain mandatory;
none grants deletion, isolation or Git publication authority by implication.

## Failure-boundary supersession — 2026-10-29

The latest operator instruction replaces the blanket no-catch/no-aggregation and
global-escape requirements. Expected conditions use typed branches, not exceptions;
defaults cover declared optional absence only. The single normative owner is
[fail loud](https://github.com/datacosmos-br/agents/blob/f9161bfb/rules/runtime/fail-loud.md), including responsible translation,
causal metadata, independent outcomes, unexpected-error containment and cancellation.
[Python guidance](https://github.com/datacosmos-br/agents/blob/f9161bfb/rules/python/no-hidden-errors.md) and
[engineering core](https://github.com/datacosmos-br/agents/blob/f9161bfb/rules/architecture/engineering-core.md) consume that rule.
This changes authority, not runtime qualification or acceptance. Publication recovery
still follows the [atomic-effects supersession](https://github.com/datacosmos-br/agents/blob/f9161bfb/rules/runtime/atomic-effects.md).

## No-preexisting-debt ruling — 2026-10-30

The operator ruled on 2026-10-30 that no failure is pre-existing: every failure surfaced
while working is owned and fixed at its root, without bypass, fallback, or rollback. The
single normative owner is
[no preexisting debt](https://github.com/datacosmos-br/agents/blob/f9161bfb/rules/ethics/no-preexisting-debt.md),
approved by this ADR as a universal (route both) companion ruling.

## Operator orders — 2026-11-02

The operator issued seven universal orders in a live session on 2026-11-02, recorded in
the tracker memories `operator-rulings-2026-11-02-lint-gate-decisions`,
`operator-order-2026-11-02-complete-cycle-zero-tolerance`,
`operator-order-2026-11-02-exceptions-martial-law`,
`operator-order-2026-11-02-exceptions-axioms-only`,
`operator-order-2026-11-02-generated-patterns-from-rules` and
`operator-order-2026-11-02-structural-patterns-automatic`. Each lands as a delta in
exactly one owner; this ADR approves them as universal (every session, project and
provider) companions of the rulings above:

1. No claim without executed proof in the same turn (command, working directory, exit
   status, decisive output):
   [validate on change](https://github.com/datacosmos-br/agents/blob/f9161bfb/rules/coordination/validate-on-change.md), point 6.
2. Every pattern fix becomes one automatic engine rule, one law at a time at fleet
   scale, with exact detection, zero manual follow-up and a root-agnostic engine:
   [structural migrations](https://github.com/datacosmos-br/agents/blob/f9161bfb/rules/workflow/structural-migrations.md),
   referenced by
   [mass rewrite discipline](https://github.com/datacosmos-br/agents/blob/f9161bfb/rules/workflow/mass-rewrite-discipline.md).
3. A single change is validated through the owner's scoped, parametrized command, never
   a global run:
   [canonical commands](https://github.com/datacosmos-br/agents/blob/f9161bfb/rules/workflow/canonical-commands.md),
   "Scoped validation of one change". The bounded `flext-0029c` route is unchanged and
   no longer the only place a direct owner command is lawful for scoped validation.
4. Generated patterns come only from the generator driven by config rules, never
   hand-written, not even in generator format:
   [generators, not projections](https://github.com/datacosmos-br/agents/blob/f9161bfb/rules/workflow/generators-not-projections.md).
5. Family placement, imports, names, MRO, facades and import order are foundational and
   declaration families carry zero behavior:
   [internal clean architecture](https://github.com/datacosmos-br/agents/blob/f9161bfb/rules/architecture/internal-clean-architecture.md).
   The FLEXT-specific detail stays with the project-owned, branch-matched `flext-law`
   and its ADRs (ADR-0014); this repository declares no copy.
6. Zero tolerance for incomplete, non-functional or theoretical delivery; sessions plan
   only sufficient, executable steps that end in effective, complete-cycle deliveries;
   regressions, pattern escapes, fallbacks and compatibility layers are graver still:
   [full landing cycle](https://github.com/datacosmos-br/agents/blob/f9161bfb/rules/coordination/full-landing-cycle.md), item 7.
7. Exterminating rule exceptions is martial law; only axioms declared once in the tooling
   SSOT and enforced by tooling survive:
   [rule exceptions](https://github.com/datacosmos-br/agents/blob/f9161bfb/rules/architecture/rule-exceptions.md)
   (new rule: no existing owner declared exception policy generically, and
   `engineering-core.md` has no token headroom; scattered prohibitions in
   `scanner-closure.md` and `strict-typed-quality.md` stay mechanism-specific).

Same-cutover owner repairs: `rules/workflow/canonical-commands.md` and
`rules/architecture/engineering-core.md` already exceeded the rule token limit on the
integration branch; their "Command deadline and performance" section and remote-access
paragraph moved verbatim to `rules/workflow/command-deadline.md` and
`rules/git/remote-identity.md`, with every consumer rewired.
