---
description: Mandatory fail-loud execution protocol for every project workflow.
capsule_summary: |
  Every project applies all of these together: fail loud, no fallback, preflight
  before effects, required environment, atomic effects, causal subprocess
  propagation, no keyring, zero residue.

  A project rule may reject more inputs; it can never relax, catch, normalize,
  skip, defer or route around any of them. Existing opposing behavior is a
  blocking violation to fix at its owner, not grandfathered compatibility.
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-08-29","route:both"]'
---

# Strict execution is universal and non-optional

Every project and projected agent applies all of these policies together:

- `fail loud` (rule file);
- `no fallback` (rule file);
- `preflight before effects` (rule file);
- `required environment` (rule file);
- `atomic effects` (rule file);
- `causal subprocess propagation` (rule file);
- `no keyring` (rule file);
- `zero residue` (rule file).

A project rule may make them narrower or reject
more inputs; it cannot relax, catch, normalize, skip, defer, or route around any
of them. Existing opposing behavior is a blocking violation to exterminate at
its owner, never grandfathered compatibility.

Resolve gate applicability before invocation. A dormant external-token gate is
not executed; selecting or invoking it applies every policy above.
