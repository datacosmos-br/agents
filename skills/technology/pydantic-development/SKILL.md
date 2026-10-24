---
name: pydantic-development
description: "pydantic v2 models, validation, serialization, flext facade contracts"
metadata:
  aihub.tags: '["activation:detected","decision:ADR-0037","detect:dependency:python:pydantic","detect:dependency:python:pydantic-settings","detect:marker:pyproject.toml","effective:2026-09-08","extends:py-dev","route:project","subject:python","usage:router"]'
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
- Maximal use of Pydantic so consumers never re-validate, narrow or convert: minimal
  models composed by inheritance and composition, reusable `t` aliases, closed domains
  as `c` StrEnums, protocol-typed fields through `InstanceOf`, discriminated unions,
  library payloads validated once at their adapter, objects reused instead of
  re-validated.
- `model_rebuild` banned and cured by declaration order; `p` protocols generated from
  `m` models by flext-infra in `make gen`.
- The complete capability inventory, upstream performance guidance, internals, and the
  removal list that the ast-grep rules and `make mod` migrations enforce — every claim
  cited against the pinned upstream source tag.

Pydantic's own documentation is the external reference for behavior; this procedure is
the project law for how that behavior may be used. Runtime behavior and project-owned
configuration stay authoritative; generated files remain outputs.
