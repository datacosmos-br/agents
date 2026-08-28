---
name: config-schema-migration
description: 'configuration migration, schema cutover, consumer rewiring'
metadata:
  aihub.tags: '["provenance:agents-owned","role:migration","updates:manual","usage:router"]'
---

# Configuration Schema Migration

Read [the complete procedure](references/procedure.md) before changing a
configuration schema, serialized representation, environment mapping, loader,
validator, or generated configuration contract.

One approved migration produces one final contract. It rewires every scoped
producer and consumer, rejects the old format, deletes superseded paths, proves
idempotence, and validates the real runtime before tests. No dual read/write,
compatibility shim, fallback, silent default, or deferred cleanup is permitted.
