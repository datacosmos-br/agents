---
description:
  Production ships complete; every defect in the blast radius is adopted and fixed,
  including pre-existing ones.
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-08-30","route:both"]'
---

# Production readiness adopts every defect in scope

Apply this standard to every current and future first-party project phase, not only the
final release. External forks retain their upstream-specific delivery contract.
A phase is complete only when its full functionality works in the real
environment and is production-ready. Runtime stability means correct operation, not a
clean or globally stationary Git tree; the continuous-concurrency contract in
`rules/coordination/fix-forward-collaboration.md` always applies.

Compose `rules/architecture/engineering-core.md` for the phase-wide decision sequence,
canonical governance authority and stricter FLEXT conformance; do not copy its contract.

A version that is broken or incomplete never ships to production. Shipping is blocked
while any gate, test, check, review thread, or known defect in the change's blast radius
is red or unresolved.

- "Pre-existing", "not mine", "third-party", "cosmetic", and "out of scope" never exempt
  a defect surfaced inside the change's blast radius. Adoption is mandatory: the
  combined state is the deliverable.
- Every known error, failure, violation and pending defect is corrected in the current
  phase. Tracking an issue does not authorize carrying technical debt to a subsequent
  phase or declaring incomplete functionality ready.
- Preserve existing functionality and business rules unless an approved project plan or
  explicit operator authorization defines the change. Quality remediation is not an
  implicit authorization to change product behavior.
- Apply fixes and hotfixes through the declared integration branch in the current
  cycle, adopting compatible concurrent work. Do not leave a correction as an isolated
  patch or defer its integration to a later phase.
- Tests confirm observed real-environment functionality; they are not the sole source
  of truth. Test success alone never proves operational readiness or replaces direct
  evidence that the delivered public surfaces work.
- Fix defects at their canonical owner with complete cutover; never patch a symptom,
  suppress a finding, or narrow a gate to make a check pass.
- Quick fixes, fallback paths, bypasses and superficial masking never satisfy readiness;
  compose the mandatory strict-execution contract and correct the underlying cause.
- Gates evaluate the delivered state, not the delta: a green change on top of a red base
  is a red delivery. Correct the owner and rerun until the delivered state is green.
- Adopt all concurrent work in the integration lane (`git merge --no-ff`), resolve every
  review comment with runtime evidence, and prove CI green before merge; post-merge
  proof closes the increment.
- A PR merges into an integration branch only with its CI green (operator order
  2026-10-24, tracker memory
  `operator-ruling-2026-10-24-compat-warning-and-green-ci-merge`: "para PR merge para as
  branchs de integracao tem que sempre passar com o CI verde"). An administrative merge
  never lands a red or still-pending CI run; a red CI keeps the PR open and is fixed
  forward on its branch.

Compose with `rules/runtime/strict-execution.md`,
`rules/coordination/fix-forward-collaboration.md`, and
`rules/architecture/generalized-abstraction.md` (same-cutover pre-existing offender
removal).
