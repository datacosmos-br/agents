---
name: beads-worker
description: 'beads execution, scoped work, tracker workflow'
metadata:
  aihub.tags: '["activation:opt-in","decision:ADR-0008","detect:opt-in:beads-worker","effective:2026-08-29","route:agent","subject:beads","usage:router"]'
---

# Beads Worker

Activate only for a currently assigned implementation slice. Semantic graph
changes, reassignment, merge, and issue closure remain owner operations.

Before editing, verify from current evidence the issue identity and revision,
assignment, unblocked dependencies, exact file scope, existing checkout and
branch, acceptance contract, integration target, and required gates. A foreign,
stale, ambiguous, or blocked assignment stops before effects.

For managed shared work, verify the city-store root and child linked by the
local bead. Record repository evidence locally and cross-rig dependency,
handoff, producer SHA, and integration state in the shared child. Reread both at
each material checkpoint; disagreement stops effects for owner reconciliation.

Execute only the assigned slice through repository owners. Preserve concurrent
work, eliminate superseded code and rewired-consumer residue, and propagate the
first command or gate failure unchanged. Correct an in-scope owner and rerun the
invalidated native path; do not repeat unchanged, switch execution paths,
normalize red evidence, or perform a tracker mutation. Owner-only work remains
active in the same issue and is handed to that owner, never treated as closure.

Resolve Available versus Explicitly suspended from the active repository
contract. During suspension, do not invoke or replace Beads and create no
substitute tracker or ledger. Preserve evidence only in separately authorized
Git, PR, review, check, and CI surfaces. Handoff must state issue, branch, SHA,
scoped files, exact command/exit/decisive output, PR
and integration evidence, residue, and unverified owner-only work. Report ready
for review only when the slice itself is validated and residue-free; never infer
merge or closure.
