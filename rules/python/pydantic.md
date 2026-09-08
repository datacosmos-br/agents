---
globs: "**/*.py"
description: Pydantic 2 boundary law — facade-only access, obligatory model MRO presets, parse-once, fail-loud through r
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-09-08","route:both"]'
---

# Pydantic 2 boundary law

Applies to every Python project that declares `pydantic` or
`pydantic-settings`. The project's declared dependency floor is the version
authority; never assume a global Pydantic version. Full reference:
`$pydantic-development` (skill procedure).

## Access is facade-only

- In FLEXT members, import Pydantic surface only through `m`, `t`, `p`, `u`,
  `r`, `e`. flext-core is the sole owner of the `pydantic` /
  `pydantic-settings` / `pydantic-core` imports. A bare `import pydantic`
  outside flext-core is a violation.
- A capability missing from the facade is a gap to close at flext-core — never
  a reason to import directly.

## Model MRO declaration is obligatory

- Every model class extends an `m.*` preset (`FrozenModel`, `ManagedModel`,
  `StrictModel`, `StrictBoundaryModel`, `FlexibleInternalModel`,
  `FrozenValueModel`/`Value`, `Entity`, `AggregateRoot`, `TaggedModel`,
  `Metadata`, `TimestampedModel` …). Declaring a consumer model directly on the
  raw Pydantic base is a violation.
- Choose the preset by contract: read-only domain data uses frozen presets;
  mutable validated state uses `ManagedModel`; external ingress uses strict
  presets. Never hand-write a `ConfigDict` that an existing preset already
  encodes.
- Identity models extend `m.Entity` (id + timestamps + version) or compose its
  mixins in the documented order; timestamps are timezone-aware UTC.

## Protocols in p, outcomes in r

- Cross-boundary dependencies are declared as `@runtime_checkable` structural
  `Protocol` classes in the `p` family, never as concrete model or service
  types.
- Validation failures leave the boundary as `r.Fail` (`e.fail_validation`),
  carrying the original cause. Catching `ValidationError` to normalize,
  default, or retry is a violation; the only authorized conversion point is the
  `e`/`u` result boundary.

## Parse once, at the boundary

- Convert untrusted input exactly once: `Model.model_validate(data)`,
  `Model.model_validate_json(raw)` (never `json.loads` first), or a cached
  `t.TypeAdapters` adapter for non-model types. ORM/dataclass objects convert
  with `from_attributes=True`.
- `dict` and `TypedDict` never cross a public boundary as a contract; convert
  at the edge into a typed model. `pydantic.v1` is forbidden.

## Removal catalog (must not survive in code)

`model_rebuild()` (a strict fleet never needs it — fix the declaration owner
across `config`/`settings`/`c`/`t`/`p`/`m`/`u`, `base.py`, `services/`,
`api.py`, `cli.py`); `model_construct()` outside a documented owner
justification; `SkipValidation`/`PlainValidator` without a documented owner
justification; the runtime `serialize_as_any=True` flag (use
`polymorphic_serialization=True` or per-field `SerializeAsAny`); v1-style
`@validator`; `@classmethod` after model validators; duplicated local
`TypeAdapter` instances; stdlib `json` at model boundaries; `os.environ`
access and copied config/settings values in leaf modules.
