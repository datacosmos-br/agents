---
name: flext-service
description: "flext service composition, service wiring, dependency injection"
metadata:
  aihub.tags: '["activation:detected","decision:ADR-0014","detect:dependency:python:flext-core","detect:selected-tag:flext","effective:2026-09-18","extends:flext-development","route:project","subject:flext","usage:on-demand"]'
---

# FLEXT Service Composition

Activate for a detected internal FLEXT consumer when declaring a service on the
`FlextService` facade, wiring its dependencies, or changing its lifecycle:
subclass declaration, `c`/`t`/`p`/`m`/`u` facade injection, singleton access,
settings injection, or replacing hand-rolled wiring with the provided kernel.
Do not activate for `FlextResult` operation selection (`flext-result`), CLI
command wiring (`flext-cli`), plain Python classes outside a flext-core
consumer, or unrelated FLEXT layout changes.

Load `$flext-development` and its ancestors first: `$solid`, `$py-dev`, then
`$flext-development`. This child owns only service composition, not Result
operation choice, route tables, architecture, or general exception policy.
Apply `$yagni` to proposed abstractions.

Ground every edit in the consumer's own sources first: the kernel is
`flext-core/src/flext_core/service.py`, the facade aliases live in
`flext_core/__init__.py`, and each project mirrors them in its package
`__init__.py` and `base.py`. Confirm the consumer's flext-core version exports
the same names before relying on any member below.

Declare `class XService(FlextService[TResult])` — the root is also exported as
`s` — or extend the per-project `Flext<X>ServiceBase`, which already pairs `s`
with the project utilities (one proven shape: `class ...(s, u.DbOracle)`).
Override `execute() -> p.Result[TResult]`; the inherited default raises
`NotImplementedError`. Type payloads with `p` protocols, build results with
`r`, model commands with `m`, and read constants, typings, and utilities only
through `c`, `t`, and `u`. Never import `flext_core` internal modules across
package boundaries.

Lifecycle is a per-class singleton owned by the kernel: `__init_subclass__`
gives every concrete subclass a `_instance` slot, `fetch_global()` builds and
returns the shared instance under a re-entrant lock, and `reset_for_testing()`
drops the slot between tests. Inherit both accessors from the root —
ENFORCE-057 rejects per-project redeclaration. Expose a module-level
`api = XService.fetch_global()` only where a shared entry point already
exists. For an isolated instance, construct with the inherited mixin fields
`runtime_settings=`, `settings_type=`, or `settings_overrides=`; call
`with_settings(settings)` for a snapshot cloned from the passed `p.Settings`.

Compose dependencies instead of reimplementing them: accept a services facade
as a parameter (the proven dispatcher shape), return `p.Result` from public
methods, and map `m` command types to handler callables. Register handlers
through the container dispatcher —
`cls._container_type.shared().dispatcher().unwrap()` plus
`register_handler` — wrapping plain payloads with `r[...].ok(...)`. Keep
effects inside `execute()` or its registered handlers; keep outward signatures
on `p`/`t` types.

Missing evidence blocks the change: if container registration semantics,
settings precedence, or a dependency's result type are not visible in the
consumer's sources, ask for the exact contract. Never re-implement the
singleton kernel, invent a service locator or base class, hand-roll settings
cloning, or run a broad stylistic refactor.

Remember: subclass `FlextService[T]`; override `execute()` returning
`p.Result[T]`; inject through the `c`/`t`/`p`/`m`/`u` facades; obtain shared
instances with `fetch_global()`; isolate tests with `reset_for_testing()`;
snapshot settings with `with_settings()`. The kernel's conveniences are not a
license for extra global mutable state.
