---
description: Runtime-bearing work is proven on the real running system (tmux counts), plans carry a recovery path, and a broken runtime outranks every other task.
metadata:
  aihub.tags: '["decision:ADR-0034","effective:2026-10-03","route:personal"]'
---

# Runtime stability pact

All work on runtime-bearing surfaces — ai-hub, flext, Gas City, Hermes, and
their deployments and projections — obeys three non-negotiable terms.

## Terms

1. **Prove it on the real system.** Completion requires validating the
   changed surface against the running system: exercise the real consumer,
   or observe a real session through tmux. Green gates, passing tests, and
   CI are bookkeeping; they never substitute the runtime observation.
2. **No effect without a recovery path.** A plan that touches a live
   runtime declares, before its first effect, which owning verb restores
   service and what aborts the operation. No known recovery path, no
   execution.
3. **Broken runtime first.** Finding the runtime damaged — whoever caused
   it — makes restoring service through the owning verbs the immediate next
   action; every other objective yields until service is back.
4. **Route around broken owners, record the dependency.** If a deployment
   owner is broken (stale release, failing gate), dependent work uses
   native reversible mechanisms and tracks the dependency; it neither
   bypasses the owner with hacks nor waits silently.
5. **Versions move only through generated locks.** Fork and toolchain
   versions are never swapped by hand — not binaries, not pins, not
   toolchain builds. New versions arrive exclusively through the declared
   upgrade path (`make upg` regenerating locks) and are re-provisioned by
   their owners.
6. **Retired projections that break a consumer are live defects.** A
   removed-but-on-disk config, pointer, or generated file that a consumer
   parses or loads is an active breakage owned by the retire-er — even when
   every tracked gate is green (working example 2026-10-03: an ignored
   orphan config holding an instruction pointer kept a whole agent runtime
   unparseable while the full check suite passed).

## Boundaries

- The proof obligation composes `validate-on-change` and
  `runtime-is-reality`; it does not weaken them.
- Recovery uses owning verbs only — no hand-editing generated state, no
  `doctor --fix` where prohibited by the project boundary.
