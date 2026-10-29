---
globs: "**/*.py"
description:
  Pydantic 2 boundary law — facade-only access, obligatory model MRO presets,
  parse-once, fail-loud through r
metadata:
  aihub.tags: '["decision:ADR-0037","effective:2026-10-05","route:both","supersedes:ADR-0008"]'
---

# Pydantic 2 boundary law

Applies to every Python project that declares `pydantic` or `pydantic-settings`. The
project's declared dependency floor is the version authority; never assume a global
Pydantic version. Full reference: `$pydantic-development` (skill procedure).

## FLEXT Mypy policy

The live operator mandate is recorded verbatim in the canonical agents tracker memory
`operator-ruling-20261005-mypy-pydantic2`; the physically resolved `decision:ADR-0037`
tag records this rule's approval lineage. Pydantic 2 and the `pydantic.mypy` plugin are
mandatory throughout FLEXT. The canonical typed tooling configuration in flext-infra owns the
policy; generated profiles, command invocations, and consumer overlays must preserve
it. Missing or empty plugins, `pydantic.v1.mypy`, and overlays that weaken the policy
are defects, not defaults or alternate execution routes.

Suspend exactly the Mypy diagnostics `prop-decorator` and `call-arg` at that owner.
This explicit exception does not authorize any other diagnostic suspension, Pyright
relaxation, per-file ignore, or local suppression. Keep every other gate strict.

Treat source changes made to accommodate these two diagnostics as regression
candidates. Prove their cause and survival on the current integration tip, then restore
only the affected hunks by a new fix-forward commit. Preserve independent architecture,
validation, factory, and immutable-data corrections; never restore a whole historical
file or adopt a mixed-policy branch blindly. Validate the restored public behavior,
lint and typing, and regenerated consumer configuration before integration. A checker
exception never substitutes for Pydantic runtime validation.

## Access is facade-only

For a static/runtime discrepancy, follow the `pydantic-development` procedure's
Static/runtime typing diagnosis section. Reproduce the public consumer and
resolved analyzer environment before assigning a false-positive classification;
the existing diagnostic exceptions above do not authorize another suppression.

- In FLEXT members, import Pydantic surface only through `m`, `t`, `p`, `u`, `r`, `e`.
  flext-core is the sole owner of the `pydantic` / `pydantic-settings` / `pydantic-core`
  imports. A bare `import pydantic` outside flext-core is a violation.
- A capability missing from the facade is a gap to close at flext-core — never a reason
  to import directly.

## Model MRO declaration is obligatory

- Every model class extends an `m.*` preset (`FrozenModel`, `ManagedModel`,
  `StrictModel`, `StrictBoundaryModel`, `FlexibleInternalModel`,
  `FrozenValueModel`/`Value`, `Entity`, `AggregateRoot`, `TaggedModel`, `Metadata`,
  `TimestampedModel` …). Declaring a consumer model directly on the raw Pydantic base is
  a violation.
- Choose the preset by contract: read-only domain data uses frozen presets; mutable
  validated state uses `ManagedModel`; external ingress uses strict presets. Never
  hand-write a `ConfigDict` that an existing preset already encodes.
- Identity models extend `m.Entity` (id + timestamps + version) or compose its mixins in
  the documented order; timestamps are timezone-aware UTC.
- Models own data invariants through native `m.field_validator`, `m.model_validator`,
  serializers and computed fields; business behavior and effects belong to `u`/services.
  Configuration merging, nested containment and facade MRO are distinct contracts.

## Protocols in p, outcomes in r

- Cross-boundary dependencies are declared as `@runtime_checkable` structural `Protocol`
  classes in the `p` family, never as concrete model or service types.
- Automatic model/service projection follows the project's accepted branch-matched
  ADR-018 contract and the `pydantic-development` projection procedure. Projected
  structural types never replace their originating runtime validation or authored DI
  port owners.
- Validation failures leave the boundary as `r.Fail` (`e.fail_validation`), carrying the
  original cause. Catching `ValidationError` to normalize, default, or retry is a
  violation; the only authorized conversion point is the `e`/`u` result boundary.

## Parse once, at the boundary

- Full closed string domains use the existing `StrEnum` type. `Literal` remains
  appropriate for a proper subset or discriminator, never an exhaustive mirror
  of the enum. Strict Python producers supply enum members; raw JSON enters
  `model_validate_json` once. No `Field(strict=False)`, retry or serialization
  round-trip to evade a strict input contract.
- Resolve enum storage, Python read/write types and JSON representation from the
  selected branch-matched FLEXT ADR-005/ADR-028 contract. Do not revive the
  superseded primitive-storage instruction from a copied skill or an old receipt.
  Validate defaults at the preset owner and preserve the source model's actual
  read/write contract in generated protocols.
- Reuse native nested models, generic specializations, presets and schema hooks.
  Existing `t.Port`/`InstanceOf` runtime checks do not prove method signatures;
  preserve static protocol checking and real consumer proof. Do not duplicate
  their runtime narrowing locally.
- A serializable payload projection delegates the original concrete annotation
  through `GetPydanticSchema`; it is not the schema-excluded FLEXT DI `t.Port`.
  Unresolved generic ports fail, never select an unconstrained schema. Required
  schema completeness after import is not satisfied by a later deferred build.
- Railway callback exceptions retain their original cause and traceback. Only
  the existing declared error boundary converts validation errors into results.

- Convert untrusted input exactly once: `Model.model_validate(data)`,
  `Model.model_validate_json(raw)` (never `json.loads` first), or a cached
  owner-provided adapter for non-model types. Runtime construction belongs to
  `u`; `t` owns the adapter annotation. ORM/dataclass objects convert with
  `from_attributes=True`.
- `dict` and `TypedDict` never cross a public boundary as a contract; convert at the
  edge into a typed model. `pydantic.v1` is forbidden.
- A validated mutable instance can later become invalid: frozen is shallow, assignment
  validation does not observe container mutation, and validating an existing instance
  normally does not revalidate it. A changed trust boundary uses its declared native
  revalidation policy, never a dict/JSON reconstruction or unchecked copy.

## Removal catalog (must not survive in code)

`model_rebuild()` (a strict fleet never needs it — fix the declaration owner across
`config`/`settings`/`c`/`t`/`p`/`m`/`u`, `base.py`, `services/`, `api.py`, `cli.py`);
`model_construct()` outside a documented owner justification;
`SkipValidation`/`PlainValidator` without a documented owner justification; the runtime
`serialize_as_any=True` flag (use `polymorphic_serialization=True` or per-field
`SerializeAsAny`); v1-style `@validator`; `@classmethod` after model validators;
duplicated local `TypeAdapter` instances; stdlib `json` at model boundaries;
`os.environ` access and copied config/settings values in leaf modules.
