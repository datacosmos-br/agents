# Pydantic catalog — capabilities, performance, experimental policy

Citations are versioned research references, not the project's dependency floor:
`@v2.14.1` denotes `pydantic/pydantic` and `@v2.15.0` denotes
`pydantic/pydantic-settings`. Re-verify availability, facade exposure and semantics
against the selected project before use.

## 1. Type ownership and capability inventory

- Domain aliases are PEP 695 `type X = ...` (or `Annotated`) declarations in `t`,
  never copied into consumers. Reuse an originating domain contract such as
  `t.JsonPayload` instead of redeclaring it. A generic collection synonym is not a
  domain contract: native `Sequence[T]`, `Mapping[K, V]`, `list[T]`, `dict[K, V]`
  and fixed or variadic tuple annotations preserve their distinct contracts.
- For FLEXT, the 2026-10-28 generic collection-wrapper retirement is owned by
  [ADR-028 Decision 7](https://github.com/flext-sh/flext/blob/0.12.0-dev/docs/architecture/adr/028-facade-boundary-orchestrators-declarative-enforcement.md#decision-7)
  and tracker memory
  `operator-ruling-2026-10-28-generic-typing-wrapper-cutover`. Complete consumers,
  rules, templates and documentation before accepting the cutover. Preserve
  tuple arity, positional element types, mutability and validation metadata.
  Domain aliases and external typing constructs such as PEP 747 `TypeForm`
  remain with their owners; this is not a ban on generic domain contracts.

- Use the internal typed surface first: `t.NonEmptyStr`, `t.PositiveInt`,
  `t.StrictInt`/`t.StrictStr`/`t.StrictFloat`, `t.JsonValue`, `t.JsonMapping`,
  `t.NonNegativeInt` — before writing a new alias; a new alias that duplicates an
  existing `t` member is a violation.
- Model annotations use the originating domain types and reusable `t` constraints;
  `Any`, `object`, bare `dict` and unparameterized collections are not contracts.
  A typed native container retains its actual item, mutation and tuple-arity contract.
  `InstanceOf[T]` validates a runtime class, not method signatures or nested payloads;
  use the selected DI port owner when that is the contract.
- Generic models parameterize explicitly (`m.RootModel[RootValueT]`-style);
  unparameterized generics on fields are violations.
- A generic declaration may keep a type parameter until specialization; an admitted
  value must have its declared concrete, bound, constrained or default contract.
  Never substitute `Any` for an unresolved port. Preserve source generic arguments,
  nested aliases and validators through projection, without a parallel type registry.

| Capability | Use it for | Reference |
| --- | --- | --- |
| `ConfigDict` presets (`m.*`) | one configuration contract per preset, inherited | `pydantic/config.py:34@v2.14.1` |
| `Field` metadata | constraints, aliases, `discriminator`, `frozen`, `exclude`, `exclude_if`, `default_factory` (may take validated data) | `pydantic/fields.py:1327-1366@v2.14.1`; `_fields.py:844-857` |
| `Annotated` aliases (`type X = Annotated[...]`) in `t` | reusable constraints + validators + serializers; one `$defs` entry | `docs/concepts/types.md:203-260@v2.14.1` |
| `StringConstraints` | strip/case/length/pattern/`ascii_only` on `str` | `pydantic/types.py:699-756@v2.14.1` |
| `AfterValidator` / `BeforeValidator` / `WrapValidator` | reusable validation inside `t` aliases | `pydantic/functional_validators.py:30,91,258@v2.14.1` |
| `field_validator` / `model_validator` (`after` = instance method) | per-model invariants | `functional_validators.py:375-493,735-743@v2.14.1` |
| `PlainSerializer` / `WrapSerializer` / `field_serializer` / `model_serializer` | output shape owned by the type | `pydantic/functional_serializers.py:21,91,224-230,355-361@v2.14.1` |
| `computed_field` | derived read-only values serialized with the model | `pydantic/fields.py:1865-2060@v2.14.1` |
| Discriminated unions (`Field(discriminator=)`, `Discriminator` + `Tag`) | polymorphic payloads, O(1) dispatch, exact narrowing | `docs/concepts/unions.md:18,188-258@v2.14.1` |
| `StrEnum` field types and `Literal[c.X.MEMBER]` tags | closed domains; enum tags work as discriminators | `tests/types/unions/test_discriminated_union.py:406-434@v2.14.1` |
| `InstanceOf[T]` | field typed by a class or `@runtime_checkable` protocol without `arbitrary_types_allowed` | `functional_validators.py:760-817@v2.14.1`; `tests/test_types.py:1861-1886@v2.14.1` |
| `RootModel[T]` | root payloads (lists, scalars) as models | `pydantic/root_model.py:34-118@v2.14.1` |
| Generic models (`BaseModel, Generic[T]`) | parametrized containers, cached per parametrization | `pydantic/_internal/_generics.py:57-144,464-553@v2.14.1` |
| `TypeAdapter` (module-level) | non-model types: unions, collections, scalars | `pydantic/type_adapter.py:160-678@v2.14.1` |
| `model_validate_json` / `TypeAdapter.validate_json` | single-pass JSON ingress in Rust | `docs/concepts/performance.md:8-19@v2.14.1` |
| `model_validate(..., from_attributes=True)` | ORM/dataclass/attribute objects | `pydantic-core/src/input/input_python.rs:513-540@v2.14.1` |
| Validation and serialization `context` | per-call data instead of globals | `docs/concepts/validators.md:638-663@v2.14.1`; `serialization.md:505-533` |
| `polymorphic_serialization` | subclass-aware dumps (models/dataclasses) | `pydantic/config.py:1209@v2.14.1`; `serialization.md:616-644` |
| `SecretStr` / `SecretBytes` | credentials; masked repr/JSON, constant-time compare | `pydantic/types.py:1819-1858@v2.14.1` |
| `FailFast` | stop sequence validation at first error (documented trade-off) | `pydantic/types.py:3370-3403@v2.14.1` |
| `validate_call` | validated public entry points (cost per call, schema built once) | `pydantic/_internal/_validate_call.py:86-137@v2.14.1`; `validation_decorator.md:410-418` |
| `MISSING` sentinel | explicit absence distinct from `None` — import from `pydantic` | `pydantic/experimental/missing_sentinel.py:18-25@v2.14.1` |
| pydantic-settings sources | env/dotenv/secrets/YAML/TOML/JSON/pyproject/CLI with deep merge | `pydantic_settings/__init__.py:5-29@v2.15.0` |

## 2. Performance within the existing contract

- Validate JSON through the direct entry points (`model_validate_json`,
  `TypeAdapter.validate_json`) — a single Rust-side pass.
- Reuse adapters through their existing native owner; do not add a second cache.
- Use concrete containers when the existing domain promises them. An optimization
  does not authorize replacing a read-only `Mapping`, fixed tuple or mutable sequence
  with a different contract. Preserve genuine union semantics; tagged variants may
  use native discriminators, not guessed tags added to accelerate validation.
- Discriminated unions (`Field(discriminator=...)`) narrow at runtime through the
  literal `kind` check; after it, attribute access is type-safe. A defensive `getattr`
  fallback after narrowing hides drift from the union contract and is a violation.
- Where the selected project requires complete declarations at import, a
  `defer_build=True` preset is a producer defect. Lazy module loading does not
  waive schema completeness once that module loads. Elsewhere, upstream support
  for deferred building is a capability, not automatic project authorization.
- The official "use `TypedDict` over nested models" performance advice is rejected:
  `TypedDict` is not a FLEXT contract. The conforming alternatives are frozen presets,
  narrower models, and adapter reuse.
- Preserve the selected preset's string-cache and mutability settings. An upstream
  optimization does not authorize a consumer override or automatic feature enablement.

Profile the real consumer before tuning validators, adapters or nested payloads;
compare cold and unchanged execution with the same semantics and inputs. Native
capabilities are chosen for the current contract, not enabled as a feature checklist.
Reference: [v2.14.1 performance guidance](https://github.com/pydantic/pydantic/blob/v2.14.1/docs/concepts/performance.md).

## 3. Experimental features policy

`MISSING` sentinel, partial validation (`experimental_allow_partial`), pipeline API
(`validate_as`) and PEP 728 TypedDict extras are capabilities to evaluate, not
automatically admitted project behavior. A selected project decision must establish
the owner, version support, complete consumer contract and upgrade proof before use.
Partial or omitted invalid data never counts as full successful admission. Experimental
imports remain with the sole SDK import owner; a documentation example grants no bypass.
The absence of a runtime warning is not stability or upgrade evidence; retain the
versioned source and the selected owner's explicit decision for experimental use.

## 4. Advanced types catalog (verify the selected floor)

`StringConstraints`, `SerializeAsAny`, `FailFast`, `Discriminator`,
`InstanceOf`, `ValidateAs`, `RootModel`, `JsonValue`, `ImportString`,
`SecretStr`/`SecretBytes`,
`AliasChoices`/`AliasPath`, `computed_field`, `TypeAdapter`, `AliasGenerator`. Consumers
reach them through `m`/`t`; a missing symbol is closed at flext-core first.
This is a discovery index, not a mandate to use every API. Check the selected floor,
facade identity and consumer contract before adopting one; experimental status and
strict Python/JSON behavior are verified separately.

## 5. Removal catalog — what must not survive in code

The [removal reference](removals.md) keeps the detailed form, replacement and
versioned evidence in one table. The required boundary law remains
`rules/python/pydantic.md`; this discovery index grants no new exception or automatic
rewrite authority.

## 6. Evidence and gates

Run diagnostics, generation, repair, formatting, checks, and tests only through the root
Make dispatcher, invoking each verb directly without an apply selector. Before tests,
exercise the real runtime path (import the facade, validate a representative payload).
The boundary audit command (`$pydantic-boundary-audit`) inventories this removal catalog's
violations per repository and feeds `make mod` migrations. A claimed automatic cure
must identify its actual native rule and fixtures; the table alone does not establish
implemented coverage or semantic equivalence.
