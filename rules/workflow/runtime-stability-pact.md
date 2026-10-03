---
description: Runtime-bearing work is proven on the real running system (tmux counts), plans carry a recovery path, and a broken runtime outranks every other task.
metadata:
  aihub.tags: '["decision:ADR-0034","effective:2026-10-03","route:both"]'
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

## Boundaries

- The proof obligation composes `validate-on-change` and
  `runtime-is-reality`; it does not weaken them.
- Recovery uses owning verbs only — no hand-editing generated state, no
  `doctor --fix` where prohibited by the project boundary.
