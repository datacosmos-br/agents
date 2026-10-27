# ADR-0025 - Adopted workspaces and invocation-selected isolation

**Status:** Accepted; amended 2026-10-23; former isolation mandate retired.
**Date:** 2026-09-22

At 21:56:04 UTC on 2026-10-23, the operator explicitly required adoption of the
current worktree and revoked mandatory isolation: it is optional by invocation type.
The correction and exact operator words are recorded in ag-wibx.2.

## Context

The earlier record incorrectly attributed a universal isolation requirement to the
operator. It blocked work in valid existing checkouts and prompted for unnecessary
exceptions. The original bytes remain in the Git commits cited below, not as live
restart instructions in this decision.

The operator retained the canonical Beads service independently of Gas City
orchestration. Treating orchestration suspension as tracker suspension would also
discard that explicit selection.

## Decision

1. `rules/coordination/gascity.md` owns placement. Adopt the current authorized
   checkout and branch, including primary/shared contexts and compatible WIP.
   Isolation is optional and selected by the actual invocation, never inferred from
   a new task, manual execution, contention, generation or closeout. Do not ask for
   a placement exception solely because the current checkout is primary.
2. Active Gas City orchestration keeps its transactional placement owner. During
   suspension, manual worktrees use native Git on the authorized destination filesystem;
   suspension does not prohibit worktrees or authorize any city, rig, Pack, agent,
   formula, run, or session orchestration action.
3. `rules/coordination/shared-venv-guard.md` owns environment identity. The manual
   workspace provisions its own physical `.venv`; attached members declared as
   dependencies of that runtime root consume it. An independent worktree owns
   its independent environment. This is distinct from borrowing another
   workspace's environment or redirecting setup with inherited variables.
   Cache and scratch placement follow `rules/storage.md`; they are not
   environments. Worktrees never belong under `/tmp` or in backup/archive copies.
4. Orchestration and tracker activation are resolved independently. A separately
   selected and available canonical Beads service remains authoritative. A suspended
   tracker is never replaced with another store or ledger.
5. Gates, authorized checkpoints, reviewed integration and runtime proof retain
   their existing owners. Retirement applies only to disposable lanes owned for the
   invocation, never an adopted primary/shared checkout or integration branch.

This decision replaces the suspension and manual-placement restrictions in rules
previously approved under
[ADR-0008](ADR-0008-governance-bundle-as-public-facade.md), and the unconditional Gas
City placement wording in
[ADR-0023](ADR-0023-worktree-discovery-maintenance-frontier.md). The discovery frontier,
single retirement executor, active-city placement contract, and historical evidence
remain unchanged.

The 2026-10-20 reconciliation removes the earlier contradiction between one
declared workspace runtime and a separate environment for every attached member.
It preserves physical ownership and exclusivity at the actual runtime root;
neither an installed binary nor an existing directory selects that root.

## Delivery

`AGENTS.md` owns the exact packaged prelude. Coordination rules own the matching
manual-execution, environment, plan-scope, and discovery boundaries; the Git rule refers
lane placement to that same activation boundary. AI Hub consumes
`GovernanceBundle` and owns declared provider publication and installed runtime
propagation. Legacy managed project instruction blocks follow authenticated
withdrawal, not re-generation. Source edits or a successful package load alone do
not prove consumer propagation.

## Correction — 2026-10-23

The canonical placement owner is
[`rules/coordination/gascity.md`](../../rules/coordination/gascity.md).
Consumers reference that owner rather than invent isolation from a historical
record or campaign profile. Explicit worktree-mode calls and assigned city jobs
retain their invocation-selected placement and physical environment contracts.

Git evidence identifies commit
`36367abdcefed3efc62149a9ae26bb361dac44e1` (2026-09-22,
`[WIP] fix(governance): require isolated manual worktrees`) as the introduction
of the blanket manual-placement rule into this ADR, the strict prelude and
coordination consumers. Its assertion of operator authority is not independent
proof of that authority. Commit
`3b7291b8f0e30ded1a5f1966f3a3089beaf06770` (2026-10-20) later made dedicated
manual isolation a default with a placement override; that default is also
superseded by the current correction.

Orchestration/tracker selection remains independent. Actual runtime-root
environment ownership and security remain with `shared-venv-guard`; all tracked,
index and untracked WIP preservation, integration and safe existing-worktree
retirement remain with their Git owners. No deletion, new isolation, provisioning
or Git publication is authorized by this amendment. Source bundle validation and
AI Hub's transactional installed delivery remain separate receipts.
