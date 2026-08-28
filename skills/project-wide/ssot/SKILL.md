---
name: ssot
description: 'Select one writable authority when facts, configuration, or projections have competing owners.'
license: MIT
metadata:
  aihub.tags: '["provenance:agents-owned","role:governance","updates:manual","usage:router"]'
  version: 1.0.0
---

# SSOT

Enforce exactly one writable authority for each surviving fact, policy, schema,
contract, configuration value, or generation contract. Every other representation
must be a typed consumer, deterministic projection, disposable cache, or evidence;
it must never become a competing writer or fallback authority.

Consume the `search-first` evidence packet after `yagni`, elect the authority and
projection contract, then hand that map to `solid`, implementation, and `dry`.
Accept one convergence recheck after rewiring; the global order remains owned by
`search-first`. Read the [authority procedure](references/procedure.md) whenever
the affected graph contains duplicate constants, schemas, config, generated files,
mirrors, docs with mutable values, dual reads/writes, or ambiguous ownership.

Do not synchronize competing authorities, choose an owner by convenience, or keep
old and new paths together. Runtime proves behavior and tests verify it; neither
silently replaces the declared source owner. Missing ownership, precedence,
generator, consumer, or runtime evidence blocks mutation loudly.
