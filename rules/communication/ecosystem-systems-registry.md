---
description: One linked ecosystem — every runtime registers here, is addressable, and coordinates by formal agreement before shared infrastructure moves.
metadata:
  aihub.tags: '["decision:operator-ruling-2026-10-03", "effective:2026-10-03", "route:both"]'
---

# Ecosystem systems registry and formal agreements

The operator's fleet is ONE linked ecosystem. This registry is the single place a
new runtime declares itself, gains an addressing contract, and accepts the binding
rules (this file, ecosystem-synergy, runtime-integrity-gate, inter-session-mail,
fix-forward-collaboration). "Not registered" never means "outside the rules" — it
means the runtime is represented by its owner until registration.

## Registered systems

| System | Identity | Addressing | Liveness channel | Runtime-validation duty |
| --- | --- | --- | --- | --- |
| Gas City (city, rigs, dispatchers, witnesses, dogs, mayor) | registered gc aliases | `gc mail <alias>` | gc mail / city events | yes — city commands in tmux/real runtime |
| ZCode (CLI sessions, this class) | session alias on the shared tracker | gc mail + shared tracker beads | tracker heartbeats + mail | yes — every landed change proven in real runtime |
| Kilo Code (IDE sessions) | IDE session + shared tracker | shared tracker beads + gc mail via owner | tracker heartbeats | yes — same duty as ZCode |
| Hermes | bridge owner: the operator | operator-relayed gc mail | owner message | bridge owner carries the contract |
| WhatsApp | bridge owner: the operator | operator-relayed gc mail | owner message | bridge owner carries the contract |
| future runtime | register here on attach | owner-provided bridge | owner message | accepts every binding rule on attach |

A runtime without a registered alias is represented by its declared owner; the
owner carries agreements INTO it and outcomes OUT of it. Registration is one row
here plus the declared addressing — nothing else.

## Formal agreements are the only cross-system mutation contract

A mutation to infrastructure other systems depend on — tracker stores and their
schema versions, shared daemons and their ports, toolchains on the fleet PATH,
deployed surfaces in agent homes, city config, generator templates — follows:

1. `[coord] agreement <topic>` states: what moves, the exact store/tool/surface,
   the new version, every system it can break, the ack deadline (default 10
   minutes), and the proposed cure if a dependent breaks.
2. Affected systems ACK in-thread, or the announcer executes when the deadline
   expires. An objection stops the mutation until adjudicated.
3. The executing system posts `[coord] landed <what> <version>` with sealing
   evidence and names every binary/session that must upgrade before its next call.
4. A system broken by the mutation announces `[coord] blocker` with the exact
   error and does not loop retries against the moved target nor mask the skew —
   the cure upgrades the dependent through its own declared path (locks, never
   hand swaps).
5. Agreements and blockers are referenced from the beads that track the work:
   the bead is the ledger, the mail thread is the contract.

Working example (2026-10-03): a tracker store migrated to schema v69 without an
agreement; every rig dispatcher driving the older embedded bd failed its work
query in a loop until the upgraded library line landed on the fork's release
lane. The protocol above exists to make that incident structurally impossible.

## Fix forward, adopt always — across systems, not just lanes

Every contribution from any registered system is owned input: attribute, preserve
compatible intent, integrate through the integration lane, supersede with
evidence. A system discovering another's in-flight work does not seize it — it
declares, coordinates in-thread, and adopts only what the liveness rule marks
abandoned (no message today).
