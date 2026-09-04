---
name: dependency-injection
description: 'dependency injection, typed ports, explicit composition roots'
license: MIT
metadata:
  aihub.tags: '["activation:detected","decision:plan-00","detect:selected-tag:internal","domain:architecture","effective:2026-09-04","policy:fail-loud","policy:no-fallback","policy:strict-execution","provenance:agents-owned","route:project","updates:manual","usage:router"]'
---

# Dependency Injection

Activate only for an internal project with a concrete dependency boundary.
Reuse the project-owned protocol or define the smallest consumer-owned typed
port, pass dependencies explicitly by constructor or parameter, and select the
implementation once at the API, CLI, worker, or daemon composition root.

Reject service locators, globals, shared mutable containers, string keys,
ambient context, import-time wiring, introspective auto-registration, hidden
fallback providers, and tests that patch private construction. Pure values and
stateless functions do not justify a container or interface.

Never activate for `third_party_fork`; preserve the upstream DI style.
