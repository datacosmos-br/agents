# ADR-0012: Phase admission requires zero pending and fleet adoption

Date: 2026-09-06 Status: Accepted; reconciled 2026-10-26
Rule: `rules/workflow/phase-admission-protocol.md`

## Context

During the crg-autopilot epic (2026-09-06) work repeatedly collided with concurrent
lanes: fixes already existed on open PRs, worktrees carried newer compositions, and
inherited WIP contained both intentional retirements and incomplete restructurings.
Advancing phases with red gates, untracked warnings, or unpushed WIP produced
integration debt that cost more than the original work.

## Decision

1. Reconcile authority, owners and evidence at every phase start. A phase closes only
   with zero pending items: required failures, warnings and missing proof resolved at
   root cause and revalidated. A bead records pending work; it never clears admission.
   Applicability follows `rules/testing/observable-runtime.md`.
2. Before any new phase begins, the fleet is swept for existing fixes — open PRs,
   branches, worktrees — and the newest correct side is adopted with `merge --no-ff`
   under the canonical Git owner, without cherry-pick or history rewriting. Adoption
   never imports dead code, fallbacks, compatibility shims, or orphaned files;
   retirements are completed, not
   reverted.
3. Adopted tests are rewritten to the governing rules before entering the tree; tests of
   retired surfaces are deleted with the surface.
4. Preserve WIP under `rules/coordination/fix-forward-collaboration.md`. Authorized
   publication and integration follow `rules/git/gitflow-branch-pr.md`, including its
   green-slice checkpoint, gated PR and merged-SHA evidence. This decision grants no
   direct integration push or publication authority.
5. Resolve commands through `rules/coordination/operator-precedence.md`: reconcile
   stale lower authority and surface genuinely incompatible current intentions before
   effects, never elevate recorded law over the live operator request.

## Consequences

- "Pre-existing", "cosmetic", and "later" are removed from the vocabulary of phase
  closure.
- Concurrent-lane collisions become adoption decisions made explicitly at merge time
  with the newest-correct rule, instead of accidental textual merges.
- Current authority is reconciled before effects, preserving operator precedence and
  the audit trail without reviving superseded publication or closure instructions.
