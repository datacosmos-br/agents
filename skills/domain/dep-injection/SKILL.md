---
name: dep-injection
description: "dependency injection, typed ports, explicit composition roots"
license: MIT
metadata:
  aihub.tags: '["activation:detected","decision:ADR-0038","detect:selected-tag:internal","effective:2026-11-03","route:project","subject:architecture","supersedes:skill:dependency-injection","usage:router"]'
---

# Dependency Injection

Applies to every change in an internal project; a third-party fork keeps its upstream
style (`rules/architecture/checkout-topology.md`). The outcome is `rules/law.md` law 4.

- A dependency arrives by constructor or parameter, typed as the smallest port its
  consumer calls; an existing project protocol is reused first.
- The implementation is chosen once, at the API, CLI, worker or daemon composition root.
- No dependency is found through a string key, ambient context, shared mutable
  container, import-time wiring, auto-registration or hidden fallback provider.
- Pure values and stateless functions need no container or port.
