---
description: Internal projects enforce Clean Architecture and explicit dependency injection.
metadata:
  aihub.tags: '["decision:plan-00","effective:2026-09-04","route:project"]'
---

# Clean Architecture and DI for internal projects

Apply this rule only when the active project profile is `internal` or
`internal_flext`. A `third_party_fork` follows its upstream and
must not be refactored to satisfy this rule.

Internal code points dependencies inward. Domain and application policy depend
on typed ports, never concrete I/O, frameworks, process state, global registries,
or generated adapters. Concrete dependencies are selected once at an explicit
API, CLI, worker, or daemon composition root and injected by constructor or
parameter.

Service locators, shared mutable containers, hidden singleton access, runtime
auto-registration, import-time wiring, and lookup by string are violations.
Create no empty layers or speculative abstractions: a pure value needs no port,
while every real external dependency requires one owned typed boundary.
