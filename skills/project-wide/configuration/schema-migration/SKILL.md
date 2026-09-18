---
name: schema-migration
description: "configuration migration, schema cutover, consumer rewiring"
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-08-29","supersedes:skill:config-schema-migration","usage:router"]'
---

# Configuration Schema Migration

Read `the complete procedure` (skill file) before changing a configuration schema,
serialized representation, environment mapping, loader, validator, or generated
configuration contract.

One approved migration produces one final contract. It rewires every scoped producer and
consumer, rejects the old format, deletes superseded paths, proves idempotence, and
validates the real runtime before tests. Canonical calculated defaults are declared once
and omitted from environment variables, settings, parameters, arguments, and persisted
config. Only non-derivable current values are required. No dual read/write,
compatibility shim, fallback, competing or default-on-error value, or deferred cleanup
is permitted.
