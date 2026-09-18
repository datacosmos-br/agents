## 1. Types and annotations

- Aliases are PEP 695 `type X = ...` (or `Annotated`) declared in `t`, never inline at
  consumers, never re-declared per module:

```python
type JsonPayload = t.JsonValue | t.JsonMapping | t.SequenceOf[t.JsonValue]
```

- Use the internal typed surface first: `t.NonEmptyStr`, `t.PositiveInt`,
  `tp.StrictInt/StrictStr/StrictFloat`, `tp.JsonValue`, `t.JsonMapping`,
  `t.NonNegativeInt` — before writing a new alias; a new alias that duplicates an
  existing `t` member is a violation.
- Annotations on models are precise built-ins or `t.*` aliases; `Any`, `object`,
  unparameterized collections, and `dict` are forbidden. Concrete class annotations use
  `InstanceOf[T]` only when instance identity (not structure) is the contract.
- Generic models parameterize explicitly (`m.RootModel[RootValueT]`-style);
  unparameterized generics on fields are violations.

## 2. Performance

- Validate JSON through the direct entry points (`model_validate_json`,
  `TypeAdapter.validate_json`) — a single Rust-side pass.
- Reuse adapters (catalog/`@cache`); instantiate `TypeAdapter` once per type.
- Prefer `list[T]`/`dict[K, V]` over `Sequence`/`Mapping` in contracts when the concrete
  container is known; use discriminated unions over smart unions.
- Discriminated unions (`Field(discriminator=...)`) narrow at runtime through the
  literal `kind` check; after it, attribute access is type-safe. A defensive `getattr`
  fallback after narrowing hides drift from the union contract and is a violation.
- `defer_build=True` is a bounded tool for CLI startup latency — apply at a documented
  owner, never fleet-wide, and never to mask a declaration failure (see Section 4).
- The official "use `TypedDict` over nested models" performance advice is rejected:
  `TypedDict` is not a FLEXT contract. The conforming alternatives are frozen presets,
  narrower models, and adapter reuse.

## 3. Experimental features policy

`MISSING` sentinel, partial validation (`experimental_allow_partial`), pipeline API
(`validate_as`), PEP 728 TypedDict extras: allowed only inside a documented owner with
an upgrade note; never in public contracts, never as silent defaults. Experimental
imports live in flext-core only.

## 4. Advanced types catalog (at the 2.13/2.14 floor)

`StringConstraints` (incl. `ascii_only`), `SerializeAsAny`, `FailFast`, `Discriminator`,
`InstanceOf`, `ValidateAs`, `RootModel`, `JsonValue`, `ImportString`,
`SecretStr`/`SecretBytes` (constant-time comparison in 2.14),
`AliasChoices`/`AliasPath`, `computed_field`, `TypeAdapter`, `AliasGenerator`. Consumers
reach them through `m`/`t`; a missing symbol is closed at flext-core first.

## 5. Removal catalog — what must not survive in code

| Violation                                                    | Replacement                                                   |
| ------------------------------------------------------------ | ------------------------------------------------------------- |
| `import pydantic` outside flext-core                         | `m`/`t`/`u` facade                                            |
| Consumer model on raw base + hand-written `ConfigDict`       | `m.*` preset                                                  |
| `model_rebuild()` call                                       | fix the declaration owner (Section 4)                         |
| `model_construct()`                                          | `model_validate` (owner-justified exceptions only)            |
| `SkipValidation` / `PlainValidator`                          | real validation, or documented owner justification            |
| `serialize_as_any=True` call flag                            | `polymorphic_serialization=True` / per-field `SerializeAsAny` |
| catch `ValidationError` → default/normalize                  | `r.Fail` via `e.fail_validation`                              |
| `json.loads` + `model_validate`, stdlib `json` at boundaries | `model_validate_json` / `u` JSON helpers                      |
| local `TypeAdapter(...)` per call                            | `t.TypeAdapters` cached factory                               |
| `os.environ` / process state in leaf modules                 | `settings.<Namespace>.*`                                      |
| copied config/settings values in leaf modules or `c`         | `config.<Namespace>.*` / `settings` read directly             |
| `pydantic.v1` namespace, `@validator`                        | v2 facade, `field_validator`                                  |
| `@classmethod` after model validator                         | instance method (`self`)                                      |
| `TypedDict`/`dict` as a public contract                      | `m` model or `t` alias at the edge                            |
| `Any`/`object` annotations on models                         | `t.*` alias / `p.*` protocol                                  |
| duplicate validator bodies across models                     | centralized `t` alias / `u` owner                             |
| private-module imports in tests/scripts/examples             | public facade / `tm` fixtures                                 |

## 6. Evidence and gates

Run diagnostics, generation, repair, formatting, checks, and tests only through the root
Make dispatcher, invoking each verb directly without an apply selector. Before tests,
exercise the real runtime path (import the facade, validate a representative payload).
The boundary audit command (`$pydantic-boundary-audit`) inventories Section 19
violations per repository and feeds `make mod` migrations.
