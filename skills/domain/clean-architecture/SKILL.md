---
name: clean-architecture
description: "clean architecture, inward dependencies, ports adapters"
license: MIT
metadata:
  aihub.tags: '["activation:detected","decision:ADR-0038","detect:selected-tag:internal","effective:2026-11-03","route:project","subject:architecture","usage:router"]'
---

# Clean Architecture

Applies to every change in an internal project; a third-party fork follows its upstream
(`rules/architecture/checkout-topology.md`). Ports and inward dependencies follow
`rules/law.md` laws 4 and 5.

- Domain and application code import no API, CLI, database, network, filesystem,
  framework or generated adapter code.
- A typed port belongs to its consumer; an outer adapter implements it and parses
  external input once, and the composition root at the executable edge wires both.
- No empty layer, generic repository or interface without a current consumer.
- A boundary change rewires every consumer, deletes the old construction path and is
  proven by the real entry point and the import direction.
