---
name: anti-hardcode
description: "configuration ownership, portable policy, hardcode removal"
license: MIT
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-08-29","usage:router"]'
  version: 1.0.0
---

# Anti Hardcode

Activate for operator-, deployment-, environment-, tenant-, or installation-controlled
values embedded outside their declared typed owner, including endpoints, providers,
models, credentials, databases, paths, timeouts, feature decisions, and duplicated owner
defaults.

Read the `owner migration procedure` (skill file). One confirmed hardcode blocks
delivery until the typed owner validates it, every consumer is rewired, and the literal
plus alternate lookup paths are removed.

An operational value is required only when the current workflow needs an external choice
that its owner cannot derive. A deterministic calculated default declared and validated
once by the typed owner is not fallback; consumers omit equal environment variables,
settings, parameters, and arguments.

Do not activate for a named mathematical, protocol, format, or immutable domain
invariant whose authority and tests prove it cannot vary operationally. A local constant
name alone does not make an operational value legitimate.
