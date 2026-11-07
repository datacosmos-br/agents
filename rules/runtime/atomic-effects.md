---
description: Authenticate publication, preserve committed effects and repair forward.
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-10-26","route:both"]'
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

For mass retirement, hold serialization through postcondition and atomically isolate
each root before internal reclamation. The rename is the commit point; sequential
unlinks are cleanup, not an atomic batch. Cleanup failure remains red, preserves its
manifest, and requires causal correction plus fresh preflight.

Follow `coordination/fix-forward-collaboration.md`: never restore published source,
the index or history, including effects published by the failing invocation.
Preserve the first original exception and the owner's durable publication evidence;
reconcile current inputs and repair forward. Cleanup may discard only this invocation's
unpublished staging objects and release its own locks. Never delete unknown, foreign,
live, dirty or ownership-ambiguous state.

See also: `strict-execution.md` (rule file) — aggregate parent policy.
