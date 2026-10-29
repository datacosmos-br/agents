---
description: Authenticate publication, preserve committed effects and repair forward.
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-10-29","route:both"]'
---

# Effects publish atomically

Authenticate the complete candidate before mutation, stage on the destination
filesystem, and publish through the existing owner's atomic commit points.
An incomplete publication fails the invocation; valid committed effects are not
reported as a successful complete operation.

Compose every intended change to the same destination before publishing it once.
Preserve the originally authenticated snapshot, ownership and mode. Last-writer-wins
deduplication, refreshed snapshots to bypass contention and competing publishers
violate the contract.

Reuse the authenticated capture and parsed representation within one planning
operation. Adjustable entries belong to typed declarative collections, not mirrored
per-entry properties or orchestration branches. Integrity and source/target identity
rechecks remain mandatory; efficiency never removes authentication.

For shared configuration, declarations own the permitted artifact, field, entry or
block effects. Current target bytes are preservation and ownership evidence, never a
second policy source. Preserve foreign content and syntax outside changed spans.
Native adapters own format handling; one existing planner and publisher own selection,
composition and effects. Conflicting edits fail before publication.

A satisfied declaration retains exact bytes and metadata, without a write or consumer
restart. Retirement also requires authenticated current ownership; familiar paths,
globs, age, version drift and missing markers alone grant no deletion authority.
Recheck source and target identities before commit. Activate only authorized consumers
whose declared configuration, executable binding or dependencies actually changed.
ADR-0022's 2026-10-28 minimum authenticated publication amendment owns the
catalog-publication boundary.

Generated artifacts must already satisfy their declared format and strict analysis
contracts. Repair and regenerate through the producer; a separate post-generation
fixer or manual projection edit is not acceptance.

For mass retirement, hold serialization through postcondition and atomically isolate
each root before internal reclamation. The rename is the commit point; sequential
unlinks are cleanup, not an atomic batch. Cleanup failure remains red, preserves its
manifest, and requires causal correction plus fresh preflight.

## Cooperative transaction boundary

When the operator authorizes a multi-artifact transaction, the existing operation
owner serializes its publication with the declared cooperative readers, including
Make and native refactoring readers. Those readers must use the same barrier before
observing affected artifacts; hold it through publication, postcondition verification
and recording of partial effects. Do not claim all-reader atomicity from independent
file renames: readers outside that protocol require their own verified consistency
contract. The barrier does not require a clean checkout, frozen HEAD, idle unrelated
writers or suspension of shared WIP.

**Supersession 2026-10-29 — operator order, tracked by `ag-ssut`.** The earlier
2026-10-28 permission for invocation-owned compare-and-swap compensation is historical
and no longer authorizes restoration or removal of published effects. The current
order requires preservation, adoption, cooperation and correction forward, including
the effects of the failing invocation.

Capture authenticated before-images, confirmed after-images and partial effects
through the existing transaction receipt. Keep source and target authentication,
compare-and-swap admission, scope and the cooperative barrier mandatory. On failure,
preserve the first original exception and traceback and record the unresolved effects;
repair their canonical owner forward against freshly authenticated current state.
Before-images remain causal evidence, never restoration instructions. Do not undo
published files, modes, directories, index changes or runtime effects, even when this
invocation owns them. Preserve independent edits and prior WIP; a drift requires
diagnosis and reconciliation, never replacement by a historical image.

Follow `coordination/fix-forward-collaboration.md`. Git reset/restore/revert, index or
history replacement and removal of another actor's lock are not recovery actions.
Cleanup may discard only this invocation's unpublished staging objects and
release its own locks. Never delete unknown, foreign, live, dirty or ownership-ambiguous
state. This rule specifies the contract; its publication is not evidence that a
consumer implements the barrier, receipts or fix-forward recovery. Cleanup failure is
additional evidence attached to the primary failure, never its replacement or success.

See also: `strict-execution.md` (rule file) — aggregate parent policy.
