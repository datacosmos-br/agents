---
name: clean-architecture
description: 'clean architecture, inward dependencies, ports adapters'
license: MIT
metadata:
  aihub.tags: '["activation:detected","decision:plan-00","detect:selected-tag:internal","domain:architecture","effective:2026-09-04","policy:fail-loud","policy:no-fallback","policy:strict-execution","provenance:agents-owned","route:project","updates:manual","usage:router"]'
---

# Clean Architecture

Activate only for an internal project. Read its manifest, architecture owners,
entry points, dependency graph, consumers, and tests before proposing a
boundary. Keep domain policy independent of I/O and frameworks, define typed
ports at the consumer boundary, implement them in outer adapters, and compose
the graph at the executable edge.

Do not create empty layers, generic repositories, or interfaces without a real
consumer and variation. Reject inward imports from domain/application code to
API, CLI, database, network, filesystem, framework, or generated adapter code.
Rewire every affected consumer, delete the superseded construction path, and
prove the public runtime plus import direction.

Never activate for `third_party_fork`; that profile follows upstream.
