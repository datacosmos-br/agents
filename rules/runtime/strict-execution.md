---
description: Mandatory fail-loud execution protocol for every project workflow.
capsule_summary: |
  Every project applies all of these together: fail loud, no fallback, preflight
  before effects, required environment, atomic effects, causal subprocess
  propagation, no application keyring read, zero residue.

  A project rule may reject more inputs; it can never relax, conceal a cause,
  normalize failure, skip required work or route around any of them. Opposing behavior is a blocking
  violation to exterminate at its owner, never grandfathered compatibility.
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-10-01","route:both"]'
---

# Strict execution is universal and non-optional

Every project and projected agent applies all of these policies together:

- `fail loud` (rule file);
- `no fallback` (rule file);
- `preflight before effects` (rule file);
- `required environment` (rule file);
- `atomic effects` (rule file);
- `causal subprocess propagation` (rule file);
- `no application keyring read` (rule file);
- `zero residue` (rule file).

A project rule may make them narrower or reject more inputs; it cannot relax,
conceal a cause, normalize failure, skip required work or route around any of them. Existing opposing behavior is a
blocking violation to exterminate at its owner, never grandfathered compatibility.

Resolve gate applicability before invocation. A dormant external-token gate is not
executed; selecting or invoking it applies every policy above.

A declared boundary may classify a documented native outcome or attach causal
context while preserving the original error and required failure status. It
cannot invent success, retry the operation or select another effect. Predicate
and diagnostic classification follow the canonical-command owner.

A strict ingress that declares duplicate JSON keys invalid rejects them at its
existing parser boundary before information is lost. Validating a last-key-wins
mapping afterward cannot prove that contract. Reuse the declared typed parsing
owner rather than creating another loader in a consumer.
