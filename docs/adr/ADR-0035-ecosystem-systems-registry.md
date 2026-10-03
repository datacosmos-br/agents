# ADR-0035 — Ecosystem systems registry: one linked fleet, registration and liveness

- **Status:** Accepted
- **Date:** 2026-10-03
- **Tracking:** operator ruling 2026-10-03; rule `rules/communication/ecosystem-systems-registry.md`

## Context

The 2026-10-03 fleet reactivation runs several coordinated runtimes (Gas City,
ZCode CLI sessions, Kilo Code IDE sessions, and the operator-relayed Hermes and
WhatsApp bridges) against shared infrastructure. Until now each runtime invented
its own addressing and its own liveness evidence, and an unregistered runtime
had no declared relationship to the binding rules — it could treat coordination
as optional.

## Decision

1. **One linked ecosystem.** The operator's fleet is ONE ecosystem.
   `rules/communication/ecosystem-systems-registry.md` is the registry where
   every runtime declares its identity, addressing contract, liveness channel,
   and runtime-validation duty.
2. **Registration never excludes.** "Not registered" never means "outside the
   rules" — an unregistered runtime is represented by its owner until
   registration, and accepts every binding rule on attach.
3. **Liveness is a message today.** A runtime counts as working only if it
   produced a message today (mail, event, or bridge receipt). Every lane whose
   last evidence predates today is abandoned and adoptable by any live system
   through fix-forward.
4. **Future runtimes register on attach.** A newly attached runtime registers
   in the registry with an owner-provided bridge; the registry table is the
   single addressing authority for the ecosystem.

## Consequences

- The binding rules (`cross-actor-cooperation`, `runtime-stability-pact`,
  `fix-forward-collaboration`, `inter-session-mail`) apply uniformly to
  registered and unregistered systems.
- Liveness arbitration between concurrent actors uses the registry's liveness
  channels (gc mail, tracker heartbeats, owner-relayed messages) as evidence.
- The registry's decision lineage is this ADR; later changes to registration,
  addressing, or liveness semantics amend it through a new ADR.
