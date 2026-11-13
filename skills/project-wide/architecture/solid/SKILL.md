---
name: solid
description: "solid principles, responsibility boundaries, dependency direction"
license: MIT
metadata:
  aihub.tags: '["decision:ADR-0038","effective:2026-11-03","usage:router"]'
  version: 2.0.0
---

# SOLID

Applies at a responsibility or dependency boundary the change touches; dependency
inversion is `rules/law.md` law 4.

- Single responsibility: split only where real consumers change the parts for different
  reasons; size alone is not one.
- Open/closed: a plugin or strategy point exists only for a second current
  implementation.
- Liskov substitution: every implementation keeps the contract's inputs, results,
  failures and effects.
- Interface segregation: an interface holds only what its consumer calls, with no stub
  or unused method.

No principle justifies a speculative interface, factory, plugin point or layer. A
language or framework child adds only its syntax.
