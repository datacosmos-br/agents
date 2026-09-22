# ADR-0025 — Dedicated manual worktrees during orchestration suspension

**Status:** Accepted **Date:** 2026-09-22

## Context

The operator's hook-convergence continuation explicitly requires every manual task to
use a dedicated native Git worktree and branch, including while Gas City remains
suspended. The operator also authorized correcting and propagating the global rule.
The previous strict prelude and coordination rules prohibited worktrees during
suspension, contradicting both that direction and the dedicated-worktree requirement
in [ADR-0021](ADR-0021-operator-universal-rulings-runtime-truth.md).

The operator retained the canonical Beads service independently of Gas City
orchestration. Treating orchestration suspension as tracker suspension would also
discard that explicit selection.

## Decision

1. Every manual task uses a dedicated native Git worktree, working branch, and physical
   environment. Implementation in the primary/default checkout is prohibited.
2. Active Gas City orchestration keeps its transactional placement owner. During
   suspension, manual worktrees use native Git on the authorized destination filesystem;
   suspension does not prohibit worktrees or authorize any city, rig, Pack, agent,
   formula, run, or session orchestration action.
3. Each worktree provisions its environment through its repository's setup owner.
   Borrowed environments, `/tmp` placement, and backup/archive copies remain prohibited.
4. Orchestration and tracker activation are resolved independently. A separately
   selected and available canonical Beads service remains authoritative. A suspended
   tracker is never replaced with another store or ledger.
5. Native gates, recoverable remote checkpoints, reviewed merge-commit landing, fresh
   integration ancestry proof, runtime proof, and retirement of the dedicated worktree
   remain mandatory under their existing owners.

This decision supersedes the suspension and manual-placement restrictions in
[ADR-0008](ADR-0008-governance-bundle-as-public-facade.md) and the
unconditional Gas City placement wording in
[ADR-0023](ADR-0023-worktree-discovery-maintenance-frontier.md). The discovery frontier,
single retirement executor, active-city placement contract, and historical evidence
remain unchanged.

## Delivery

`AGENTS.md` owns the exact packaged prelude. Coordination rules own the matching
manual-execution, environment, plan-scope, and discovery boundaries; the Git rule refers
lane placement to that same activation boundary. AI Hub consumes
`GovernanceBundle` and owns generated project/global instructions and installed
runtime propagation. Source edits or a successful package load alone do not prove
consumer propagation.
