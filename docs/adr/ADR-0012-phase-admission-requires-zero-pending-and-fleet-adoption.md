# ADR-0012: Phase admission requires zero pending and fleet adoption

Date: 2026-09-06
Status: Accepted
Rule: `rules/workflow/phase-admission-protocol.md`

## Context

During the crg-autopilot epic (2026-09-06) work repeatedly collided with
concurrent lanes: fixes already existed on open PRs, worktrees carried
newer compositions, and inherited WIP contained both intentional
retirements and incomplete restructurings. Advancing phases with red
gates, untracked warnings, or unpushed WIP produced integration debt that
cost more than the original work.

## Decision

1. A phase closes only with zero pending items: every failure, warning,
   and skipped check resolved at root cause or carried by its own bead
   with exact evidence.
2. Before any new phase begins, the fleet is swept for existing fixes —
   open PRs, branches, worktrees — and the newest correct side is adopted
   (cherry-pick for isolated commits, `merge --no-ff` for lanes). Adoption
   never imports dead code, fallbacks, compatibility shims, or orphaned
   files; retirements are completed, not reverted.
3. Adopted tests are rewritten to the governing rules before entering the
   tree; tests of retired surfaces are deleted with the surface.
4. WIP is pushed at every coherent increment; landing is a `merge --no-ff`
   into the declared integration branch with gates rerun on the merged
   SHA, then push.
5. Operator commands are validated against the governing authority stack;
   a genuine conflict between a command and recorded law is surfaced with
   one precise question, never absorbed silently.

## Consequences

- "Pre-existing", "cosmetic", and "later" are removed from the
  vocabulary of phase closure.
- Concurrent-lane collisions become adoption decisions made explicitly at
  merge time with the newest-correct rule, instead of accidental
  textual merges.
- An operator command and recorded law that disagree produce a visible
  question, preserving both the operator's supremacy and the audit trail
  of law changes.
