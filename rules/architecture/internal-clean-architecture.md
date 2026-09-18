---
description:
  Internal projects enforce Clean Architecture, strict FLEXT facades, and explicit DI
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-09-04","route:project"]'
---

# Clean Architecture and DI for internal projects

Apply this rule to `internal` and `internal_flext` profiles. A `third_party_fork`
retains upstream architecture.

Domain and application policy import no I/O, adapter, framework, process state, global
registry, or concrete service. They depend inward on precise typed ports. The public
`api.py` is the only composition root: it selects concrete edges once and injects them
through constructors or parameters. `cli.py` is a thin process adapter over that API.
Service locators, shared mutable containers, hidden singletons, import-time wiring,
string lookup, and auto-registration are violations. Create no empty layer or
speculative port.

For `internal_flext`, the structural MRO is exactly `c → t → p → m → u` and the
operational facade set is exactly `r`, `e`, `x`, `h`, `d`, and `s`. Every facade family
lives under `_<module>/`, begins with `base.py`, places each additional class in its own
module, and is composed through explicit inheritance. The public API composes the
required facades; parallel facades, tuple-unpacked bases, eager export routers,
compatibility namespaces, and local descriptors are prohibited.

Each module has at most 200 logical lines and exactly one top-level class. Declaration
layers are pure: `c` owns constants, `t` alone owns type aliases, `p` alone owns
protocols, `m` owns Pydantic 2 models, and `u` owns pure utilities. All structured
boundary input and output is validated by Pydantic 2 models. Public and DI contracts
contain no `Any`, `object`, `Optional`, or `dict`; use precise models, aliases,
protocols, and explicit null unions.

Settings own external input and config owns validated derivation before the facade
graph. Consumers import those owner objects directly. Local aliases, copies,
redeclarations, environment rereads, re-derivation, reverse imports, and type-only
runtime cycles are prohibited. Services receive `p` dependencies explicitly; adapters
stay outside domain/application.

flext-infra owns validation, gates, and code generation for this structure; flext-core
owns reusable runtime primitives. Correct every violation at that owner, regenerate all
consumers, prove the public runtime, and remove old code, tests, fixtures,
documentation, generated files, backups, and archives in the same cutover.
