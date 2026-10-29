---
description:
  Admission gate between execution phases — applies before starting any new phase,
  tracker item, or lane. Load when a phase or work item is about to be declared
  finished, when picking up the next phase, or when adopting concurrent work.
metadata:
  aihub.tags: '["decision:ADR-0012","effective:2026-10-29","route:both"]'
capsule_summary: |
  Carry the full declared phase through its integrated and required runtime proof;
  do not abandon its remaining population or start unrelated work beside it.
  A phase is admitted as finished only with zero pending items: required failures,
  warnings and missing proof resolved, never merely tracked. Reconcile authority,
  owners and evidence at every phase start. Publication and integration follow the
  authorized gated PR contract, never a direct integration push. Before entering
  the next phase, sweep the fleet for existing fixes first: open PRs, foreign
  branches, and worktrees may already carry the work; adopt the newest correct
  side through the merge contract owned by git/gitflow-branch-pr, never
  keeping dead code, fallback, or compatibility. Revalidate the merged SHA before
  closure. Resolve authority by operator precedence; surface genuine conflicts.
---

# Phase admission protocol

No phase, tracker item, or lane closes while anything is pending, and none opens while
adoption debt exists.

## Law

0. **Always working, one phase at a time.** The 2026-10-24 operator order
   `operator-order-2026-10-24-always-working-never-skip-phase` requires the whole
   declared population and complete delivery cycle, not a successful sample or
   local-only result. Finish required runtime restoration, applicable native
   generation/repair/check/test contracts, current-SHA CI, reviewed integration
   and post-merge proof before phase closure. An already failing runtime requires
   causal recovery in the active phase; it is not a clean-state prerequisite or
   permission to abandon remaining work. Do not start an unrelated phase beside it.
1. **Zero pending closure.** At the beginning of every phase, reconcile current operator
   intent, canonical owners, concurrent work and required evidence before dependent
   effects. A required failure, warning or missing proof is RED and remains agent-owned
   until causal repair and revalidation; tracking it never admits the next phase.
   Applicability and unmet prerequisites follow
   [observable runtime](../testing/observable-runtime.md), not an invented green receipt.
   Necessary authorized repairs continue while RED; phase advancement does not.
2. **Fleet sweep before new work.** Before starting a phase, check open PRs, branches,
   and worktrees for existing fixes of the same problem. Adopt the newest correct side:
   integrate lanes with `merge --no-ff`, without cherry-pick or history rewriting.
   Never adopt dead code, fallback, compatibility shims, or orphaned files — if the other side carries
   them, complete the retirement instead.
3. **Tests follow reality.** Adopted tests are rewritten to the governing rules (no
   mocks, no patch, no skips) before they enter the tree; tests of retired surfaces die
   with the surface.
4. **Preservation and publication.** Preserve compatible WIP under
   [fix-forward collaboration](../coordination/fix-forward-collaboration.md).
   [Branch and PR](../git/gitflow-branch-pr.md) alone owns authorized checkpoints,
   preservation refs, review gates and publication; this rule grants no Git effect.
5. **Landing contract.** Complete the authorized gated PR integration and merged-SHA
   revalidation under that owner before advancing. Local green, a tracked blocker or
   "mergeable" alone is never landed. Missing publication authority leaves delivery
   open; it never authorizes direct integration pushes or bypassing guards.
6. **Commands are validated.** Apply
   [operator precedence](../coordination/operator-precedence.md) before execution.
   Reconcile stale lower authority; surface genuinely incompatible current intentions
   before the conflicting effect, never treat old law as overriding the live request.

## Violations this rule exterminates

Starting a new phase, slice, or unrelated work while another is incomplete; skipping or
deferring any part of a cycle; leaving the project broken or its runtime failing;
pushing incomplete or red work to an integration, working, or upload branch or to a PR;
advancing a phase with red gates or untracked warnings; re-implementing a fix that an
open PR already carries; adopting a lane wholesale with its dead code; landing without
merged-SHA revalidation; retaining lower or older authority that contradicts the current
operator intent instead of reconciling its canonical owner.

The operator's 2026-10-26 amendment applies continuously to every session and task.
Its verbatim source is the operator record in `ag-h1k1`; a tracked required defect
never waives phase acceptance or the executing agent's responsibility for causal
repair.

Reconciled 2026-10-29: the 2026-10-24 no-incomplete-push and preservation-ref
orders remain routed through Law 4's Git owner. Their historical no-test wording
does not prohibit required causal diagnostics or correction revalidation while RED.
Current operator authorization governs effects within scope; no older text overrides
it, waives CI/review/runtime proof or authorizes destructive recovery.

## Precedent

2026-09-06: a review-graph autopilot epic — adoption of the governance cutover lane kept the partial-CRG-maintenance
retirement dead, reduced the gate debt 372→324 with automated `make mod` fixes, and
blocked its own integration merge until the conformance sweep closes.
