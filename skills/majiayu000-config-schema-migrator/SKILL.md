---
name: majiayu000-config-schema-migrator
description: majiayu000, config, schema, migrator, migration, atomic, strict, cutover, consumers, public-interface
---

# Majiayu000 Config Schema Migrator

This file is the activation router. Before acting, read
[the complete procedure](references/procedure.md) in full and follow it.

## Critical rules

- Treat a schema migration as one atomic cutover: owner, data, generators,
  consumers, tests, documentation, and runtime wiring change together.
- Exterminate the superseded schema and every old consumer. Never add a shim,
  fallback, compatibility alias, dual reader/writer, deprecation window, or
  hardcoded bridge for the superseded contract.
- A public-interface change is prohibited until the operator reviews and
  explicitly approves its exact contract and impact.
- Completion requires all native gates, migration idempotence, runtime proof,
  contradiction search, and a published PR containing the complete cutover.
- If any consumer cannot migrate in the same change, stop: the migration is not
  eligible to begin or land.
