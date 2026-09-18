---
name: pydantic-development
description: "pydantic v2 models, validation, serialization, flext facade contracts"
metadata:
  aihub.tags: '["activation:detected","decision:ADR-0008","detect:dependency:python:pydantic","detect:dependency:python:pydantic-settings","detect:marker:pyproject.toml","effective:2026-09-08","extends:py-dev","route:project","subject:python","usage:router"]'
---

# Pydantic Development

Apply when the active project declares `pydantic` or `pydantic-settings` as a
dependency. Composes `$py-dev` (and through it `$solid`); keep only the
Pydantic-specific delta here.

Read the `pydantic procedure` (skill file). It owns the complete reference:

- Version authority: the project's declared dependency floor, never a global assumption;
  capabilities are chosen at that floor.
- Facade-only access in FLEXT members (`m`/`t`/`p`/`u`/`r`/`e`); flext-core is the sole
  owner of Pydantic imports.
- Obligatory model MRO declaration through `m.*` presets; read-only vs mutable vs strict
  preset selection; identity models with id, UTC timestamps, and optimistic-lock
  version.
- Obligatory structural protocol declaration in `p` and railway outcomes in `r`
  (`p.Result[ModelT]`); the single authorized validation-error conversion point.
- Canonical conversions for dict, TypedDict, dataclass, and JSON payloads — parsed once,
  at the boundary.
- Validation and serialization practice at the current Pydantic floor (constraints,
  validator modes and ordering, validation context, polymorphic serialization,
  `exclude_if`).
- The complete good/bad practice catalog and the removal list that the boundary audit
  and `make mod` migrations enforce.

Pydantic's own documentation is the external reference for behavior; this procedure is
the project law for how that behavior may be used. Runtime behavior and project-owned
configuration stay authoritative; generated files remain outputs.
