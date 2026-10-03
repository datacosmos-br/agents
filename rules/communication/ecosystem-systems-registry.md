---
description: The systems registry — every runtime in the operator's linked ecosystem, its addressing, liveness channel, and validation duty.
metadata:
  aihub.tags: '["decision:ADR-0035", "effective:2026-10-03", "route:personal"]'
---

# Ecosystem systems registry

The operator's fleet is ONE linked ecosystem. This registry is where a runtime
declares itself, gains an addressing contract, and accepts the binding rules.
"Not registered" never means "outside the rules" — an unregistered runtime is
represented by its owner until registration.

## Registered systems

| System | Identity | Addressing | Liveness channel | Runtime-validation duty |
| --- | --- | --- | --- | --- |
| Gas City (city, rigs, dispatchers, witnesses, dogs, mayor) | registered gc aliases | `gc mail <alias>` | gc mail / city events | yes — city commands proven in real runtime |
| ZCode (CLI sessions) | session alias + shared tracker | gc mail + tracker beads | tracker heartbeats + mail | yes — every landed change proven in real runtime |
| Kilo Code (IDE sessions) | IDE session + shared tracker | tracker beads + gc mail via owner | tracker heartbeats | yes — same duty as ZCode |
| Hermes | bridge owner: the operator | operator-relayed gc mail | owner message | bridge owner carries the contract |
| WhatsApp | bridge owner: the operator | operator-relayed gc mail | owner message | bridge owner carries the contract |
| future runtime | register here on attach | owner-provided bridge | owner message | accepts every binding rule on attach |

## Binding rules of the ecosystem

- `cross-actor-cooperation` — gc mail coordination, lane declaration,
  agree-before-overlap, and the formal-agreement mechanics for
  shared-infrastructure mutations.
- `runtime-stability-pact` — real-runtime proof (tmux where interactive),
  recovery path before effect, broken-runtime-first, versions only through
  generated locks, retired projections that break consumers are live defects.
- `fix-forward-collaboration` + `inter-session-mail` — the integration and
  channel contracts.

## Liveness

A runtime counts as working only if it produced a message today (mail, event,
or bridge receipt). Every lane whose last evidence predates today is abandoned
and adoptable by any live system through fix-forward.
