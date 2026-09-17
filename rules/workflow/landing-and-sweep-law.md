---
description: Public-history discard, direct-to-integration pushes, and unowned reds are landing-scope governance effects with mandatory beads, inventories, and merged-SHA gates.
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-09-11","route:both"]'
---

# Landing and sweep law: discard inventory, landing ownership, red capture

Session evidence 2026-09-11 (flext conformance sweep, plan
`docs/plans/2026-09-11-flext-conformance-sweep.md`): a wip discard, a 12-file
template/test cleanup, and an abandoned midpoint investigation landed through a
direct fast-forward push to the integration branch with zero beads. The result
was technically on the tip and procedurally unlanded — coordination debt
transferred to every concurrent lane. This rule encodes what that session
violated so the failure mode cannot repeat silently.

## Discarding public history is a production effect

Rewriting shared history (`reset --hard` past a public or pushed commit,
history surgery to drop a commit) requires, before the first destructive
command, a bead that inventories every hunk being discarded and classifies it:
already re-derived elsewhere, still required and absent (must be ported back
with a test), or superseded by a newer decision (record why). A discard that
loses SSOT surgery (hermetic-env, conform writers, orchestrator paths) without
that inventory has not completed; re-derive the lost hunks before reporting
closure. Cherry-pick is not derivation proof.

## Operator pressure does not waive the landing flow

"Go to the end", "do not stop", and similar pressure instructions authorize
persistence, not rule inversion. The `full landing cycle` rule owns the delivery
path. This rule adds the repair contract: record a direct integration-branch
push as a violation and restore reviewed lane/PR provenance at the next safe
green increment; never present the direct push as compliant merely because its
diff passed gates.

## Idempotency is an SLA of the generator, not a cleanup nicety

For any change touching the generation surface, `make gen` twice from
the same tree must be byte-identical before a push. A second-run divergence is
a P0 product defect for every fleet member consuming the projections.
Instrument with file-based diffs (difflib to a log file; stdout of codegen is
flooded and yields silent-nothing evidence), fix the divergent block at its
writer, and add a convergence regression test naming that block. Publishing
through gates that cannot converge is publishing a broken scaffolder.

## Reds are captured in the turn they are observed

Every newly observed red (test, gate, runtime) gets a bead in the same turn:
the failing site, the best current root-cause hypothesis, and the observable
trigger. "Pre-existing" without a bead is not scoping — it is abandonment of
the root cause. A poorly instrumented investigation that yields nothing is not
evidence of anything; re-instrument or hand the hypothesis (with artifacts) to
the next session through the bead, never through narrative.

## Test budget is enforced on the test, never on the limit

A test executing real provisioning (mise install, uv sync) in-line violates the
budget law by construction. Fix by fixture isolation and receipt assertions;
raising the timeout limit is prohibited in all cases.
