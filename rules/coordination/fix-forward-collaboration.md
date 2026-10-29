---
description:
  Preserve concurrent work and integrate every compatible contribution forward.
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-08-29","route:both"]'
---

# Adopt the current state and collaborate by fix-forward

Treat every current authorized-repository change as owned input regardless of provenance
or age. Re-read shared files, attribute overlapping intent, preserve compatible
contributions, and adopt them through the integration lane. The combined result is the
target; provenance never exempts a defect from fix-forward.

Dirty, moving and concurrently edited worktrees are the permanent expected operating
state. Requiring clean Git, zero WIP, a stable/frozen branch or HEAD, or idle/exclusive
writers as a condition to start, continue, integrate or validate authorized work is
expressly prohibited. Never ask the operator to clean the tree, discard or stash work,
stop other actors, or commit unrelated changes to make the work possible. Adopt the
current state, coordinate bounded owners, fix forward and revalidate the combined
result. A changed snapshot requires reconciliation, not a demand for a clean or stable
repository; this prohibition does not disable atomic integrity or safety checks.
Do not create a clean checkout to evade the current shared state.

Bind validation and evidence to the bounded inputs actually observed. A missing receipt
or a gate that rejects unrelated dirty state is a concrete evidence or admission defect
to correct at its owner, never grounds to demand repository cleanup. Preserve truthful
results and specific source-safety guards; never fabricate a passing receipt.

Preserve unmanifested provider output, generated destinations, external files, and
ambiguous objects without promoting them to canonical input. Bulk adoption or
replacement requires `divergent-object adjudication` (rule file).

Never stash, reset, restore, revert, rebase, force-push, roll back code/history, or
replace shared files to remove work. Never restore published source, Git state,
the index, or history. The sole bounded exception for this invocation's own failed
publication is the explicitly authorized compare-and-swap compensation contract in
[atomic effects](../runtime/atomic-effects.md); it grants no global rollback.
Fix the canonical owner forward and preserve valid sibling gains and the original
native failure. Cleanup may discard only the invocation's own unpublished staging
objects and release its own locks.

A severe conflict exists only when two current intentions require incompatible behavior
or when preserving both would violate a higher authority. Stop before the conflicting
effect, present both intentions and their evidence, and ask the operator one precise
question. Ordinary overlap, divergence, a red gate, or integration work is not severe:
reconcile, validate, and continue forward. Unexpected state requires fresh preflight; it
proves no actor or intention and never authorizes an unchanged retry.

Concurrent changes to the branch, HEAD, index, or shared files do not require the
operator to choose an exclusive writing session. Inspect the resulting state, adopt
compatible work, and continue the authorized effect. Serialize dependent mutations and
consume each command's result before issuing the next; coordination must not become a
new approval requirement.

Compose this invariant with `shared-file coordination` (rule file),
`operator precedence` (rule file), `plan adoption` (rule file), and
`the destructive Git guard` (rule file).
