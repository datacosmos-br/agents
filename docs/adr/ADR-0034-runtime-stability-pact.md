# ADR-0034 — Runtime stability pact: real-runtime validation and no broken runtime

- **Status:** Accepted
- **Date:** 2026-10-03
- **Tracking:** bead `gc-13572e`; operator directive 2026-10-03 (consolidated)

## Context

The 2026-10-03 city reactivation surfaced two failure classes the existing
rules treat too loosely: interventions that left the runtime damaged (an
interrupted deploy killed the machine supervisor), and work declared done on
gate evidence alone. The operator made the contract non-negotiable: all work
on ai-hub, flext, and every runtime-bearing surface is validated in real
runtime (tmux sessions are a valid observation channel), and no plan may be
executed — or left finished — with a broken runtime.

## Decision

1. **Real-runtime proof, always.** Every change to a runtime-bearing surface
   (ai-hub, flext, Gas City, Hermes, their deployments and projections) is
   validated against the running system before completion: exercise the real
   surface or a tmux-observed session of it. Gates, tests, and green checks
   are bookkeeping, never the proof (they sharpen `validate-on-change` and
   `runtime-is-reality`, they do not replace them).
2. **No plan executes if it can leave the runtime broken.** A plan that
   touches a live runtime carries a recovery path before its first effect:
   which verb restores service, who is paged, and what the abort condition
   is. An intervention whose recovery path is unknown waits until it is
   known.
3. **Broken runtime outranks every other task.** Discovering damage —
   including damage caused by someone else — makes restoring service the
   next action, through the owning verbs, before any further effect.
4. **Instability upstream is routed around, never hidden.** When a
   deployment owner is broken (e.g., the ai-hub release attestation gate),
   dependent work uses native, reversible mechanisms and records the
   dependency in the tracker; it neither bypasses the owner nor waits
   silently.

## Consequences

- Session reports that claim completion must carry the runtime observation
  (command, channel, decisive output) for every touched surface.
- Deploy procedures gain a standing recovery section; a deploy without one
  is not authorized.
