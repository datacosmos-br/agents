## 1. Types and annotations

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

## 2. Performance

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

| Violation                                                    | Replacement                                                   |
| ------------------------------------------------------------ | ------------------------------------------------------------- |
| `import pydantic` outside flext-core                         | `m`/`t`/`u` facade                                            |
| Consumer model on raw base + hand-written `ConfigDict`       | `m.*` preset                                                  |
| `model_rebuild()` call                                       | fix the declaration owner; see declaration.md                 |
| `model_construct()`                                          | `model_validate` (owner-justified exceptions only)            |
| `SkipValidation` / `PlainValidator`                          | real validation, or documented owner justification            |
| `serialize_as_any=True` call flag                            | `polymorphic_serialization=True` / per-field `SerializeAsAny` |
| catch `ValidationError` → default/normalize                  | `r.Fail` via `e.fail_validation`                              |
| `json.loads` + `model_validate`, stdlib `json` at boundaries | `model_validate_json` / `u` JSON helpers                      |
| local `TypeAdapter(...)` per call                            | reusable adapter from its native `u` owner                    |
| `os.environ` / process state in leaf modules                 | `settings.<Namespace>.*`                                      |
| copied config/settings values in leaf modules or `c`         | composition-root selection and explicit injection             |
| `pydantic.v1` namespace, `@validator`                        | v2 facade, `field_validator`                                  |
| `@classmethod` after model validator                         | instance method (`self`)                                      |
| `TypedDict`/`dict` as a public contract                      | `m` model or `t` alias at the edge                            |
| `Any`/`object` annotations on models                         | `t.*` alias / `p.*` protocol                                  |
| duplicate validator bodies across models                     | `t` constraint or shared `u` behavior, registered through `m` |
| private-module imports in tests/scripts/examples             | public facade / `tm` fixtures                                 |

## 6. Evidence and gates

Run diagnostics, generation, repair, formatting, checks, and tests only through the root
Make dispatcher, invoking each verb directly without an apply selector. Before tests,
exercise the real runtime path (import the facade, validate a representative payload).
The boundary audit command (`$pydantic-boundary-audit`) inventories this removal catalog's
violations per repository and feeds `make mod` migrations.
