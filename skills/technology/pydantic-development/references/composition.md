# Model composition — identity, inheritance, protocols, domains, compression

Continues [declaration.md](declaration.md). The project's selected ADR-014/018/019/028
owners govern family composition, payload projection and service ports; this
reference explains their different use at the Pydantic boundary.

## 5. Identity models — id, timestamps, version

Use the selected public entity preset and its declared identity, timestamp and
version contracts. Resolve mixin order and effective fields from that owner before
constructing a value. The earlier supplier inventory provides a lookup checklist,
not an instruction to manufacture absent fields:

- `unique_id`: `uuid4` default, non-empty string.
- `created_at`: frozen, UTC-enforced validator, ISO 8601 JSON serializer.
- `updated_at`: set in `model_post_init` when absent; must be ≥ `created_at`.
- `version`: optimistic-lock counter with minimum validation.
- `domain_events`: `MutableSequence` event-sourcing buffer (`p.HasDomainEvents`).
- Domain events retain their declared lifecycle rather than acquiring a copied buffer.

Compose only the owner's documented mixins. Timestamp and audit fields reuse native
declarations. Under FLEXT ADR-028 Decision 14, compare entity identity explicitly by
id and preserve native model-value equality. Mutable entities remain unhashable;
frozen-model hashing still requires hashable field values.

## 6. Inheritance and MRO rules

- Explicit inheritance only; every base named. The versioned Pydantic configuration
  implementation merges base configuration rather than following Python C3. Inspect
  effective `model_config`, fields and behavior; never infer a universal mixin recipe
  from class order or repair a conflict by copying configuration locally. See
  [configuration inheritance](https://docs.pydantic.dev/latest/concepts/config/).
- Overriding a field requires an annotation; a bare `x = 1` over a parent field raises
  `model-field-overridden` (`pydantic/_internal/_fields.py:353-358@v2.14.1`).
- `model_post_init` overrides use `@override` and call `super()`.
- Preserve the selected model's native equality/hash semantics; do not install an
  identity-based pair on entities. A frozen preset can provide a field-value hash
  while native equality compares the model's values
  (`pydantic/_internal/_model_construction.py:261-262,512-525@v2.14.1`;
  `pydantic/main.py:1225-1282@v2.14.1`). Use hashable field types (`tuple`,
  `frozenset`) only when those collections match the domain contract.
- After model validators are instance methods (v2.12+ deprecated the `@classmethod`
  form):

Use the native `m.model_validator(mode="after")` instance-method contract and
return the validated model. The [boundary procedure](boundary.md#2-validation-practice--centralized-owners)
owns validator ordering, context and failure behavior.

- A validator defined on a base runs for subclasses; overriding replaces it.
- Namespace facade inheritance, data inheritance and nested containment are distinct.
  A nested model has its own configuration boundary. Frozen prevents attribute
  reassignment, not mutation of a contained list or mapping; assignment validation
  does not intercept every in-place mutation. Reuse the native collection contract.

## 7. Protocol declaration in p — obligatory

Cross-boundary dependencies are structural contracts in the `p` family, never concrete
model/service types (DIP):

- Nested inside the `FlextProtocols*` container; `@runtime_checkable class X(Protocol)`,
  extending `p.Base` when it generalizes an existing contract.
- Members are the minimal consumed capability (ISP): instance attributes and methods
  with `...` bodies and docstrings. Class-level Pydantic APIs stay on dedicated class
  protocols (`p.Model` instance API vs `ModelType`).
- Imports of `m`/`t` inside protocols are `TYPE_CHECKING`-only.
- Outcomes use `p.Result[T]`; routable messages use `CommandRoutable` / `EventRoutable`
  / `QueryRoutable`.

Model/service projection follows the accepted branch-matched ADR-018 and
[projection procedure](typing-diagnosis.md#project-owned-model-and-service-protocol-projection).
Its target coverage is not proof of implementation. Never hand-mirror an omitted
contract or replace an authored DI port with a service's projected implementation.
New ports join the existing family; consume its capability instead of the implementation.

## 8. Protocol-typed fields

A runtime collaborator uses the existing field-scoped DI annotation, such as
`t.Port[p.X]`, rather than globally allowing arbitrary payloads. Preserve its native
runtime and static contracts:

- Native `InstanceOf` checks instance/member presence. It does not prove signatures
  or nested payload validity (`pydantic/functional_validators.py:760-817@v2.14.1`).
- It is scoped to that field; the preset keeps rejecting unknown types everywhere else
  (`pydantic/_internal/_generate_schema.py:738-753@v2.14.1`).

FLEXT DI `t.Port` is schema-excluded. A serializable payload projected to `p` instead
retains its original concrete validation and serialization through its schema hook,
such as `GetPydanticSchema`. Resolve generic arguments at the owner; an unresolved
port never receives an unconstrained schema as a substitute.

Compose model data with existing admitted objects and inject runtime capabilities by
their `p` contracts through the approved port. Do not transport either through dumps,
reconstructed mappings or copied implementations. Preserve each consumer's read/write
rights: mutable operation state can be referenced by an immutable authenticated
transaction without making that state immutable or allowing transaction mutation.

## 9. Closed domains are StrEnum members of `c`

Complete closed string domains use their existing `c` `StrEnum` directly. Proper
subsets and discriminators retain their narrower `Literal` contract. This is the
operator's domain policy, not an upstream ban on literals:

- Lax mode accepts the member or its value; strict Python input requires the member;
  JSON accepts the value (`pydantic-core/src/validators/enum_.rs:104-173@v2.14.1`;
  `docs/plugins/conversion_table.py:1385-1422@v2.14.1`).
- The selected FLEXT contract centralizes `use_enum_values=False` in the governed
  presets. Python fields and dumps preserve enum members; JSON uses its native
  representation at the outward boundary. Preserve the strictness and required
  default-validation policy of each preset. Consumers do not repeat these settings.
- Discriminated unions take `Literal[c.Kind.LINE]` tags; enum members are valid
  discriminator values (`tests/types/unions/test_discriminated_union.py:406-434@v2.14.1`).

The [owning enum contract](declaration.md#flext-enum-and-schema-contracts) and the
projected model determine the concrete domain and discriminated-union members.

## 10. Minimal models, maximal reuse

The project carries the fewest models and fields that express the contracts:

- **One model per payload shape.** Near-duplicate models that differ by one field are
  merged through inheritance (a base declares the shared fields, subclasses add only
  their delta) or composition (a nested model reused as a field).
- **Reuse the admitted object.** Under the same contract and trust state, pass the
  instance directly; changed trust follows the [boundary policy](boundary.md).
- **Constraints live in types, not fields.** A constraint repeated on several fields is
  a `t` alias (`type NonEmptyStr = Annotated[str, ...]`); a field carries `m.Field(...)`
  only for field-specific facts (default, alias, discriminator, description).
- **Derived values are `computed_field`s**, not stored fields kept in sync by hand.
- **Preset first.** A model never repeats configuration its preset already encodes.
- **Defaults belong to the field owner.** Give genuinely omissible inputs their
  approved default or factory once; `T | None` alone still declares a required input.
  Never invent `None`, an empty collection or a business default to satisfy callers.
  Callers omit an owned default instead of restating it; required facts stay required.
- Use the existing `t` surface (`t.NonEmptyStr`, `t.PositiveInt`, `t.JsonValue`,
  `t.JsonMapping`, …) before declaring a new alias; a duplicate alias is a violation.

Consumers receive their validated contract; producer defects require owner repair,
not duplicated narrowing, casts, parsing or schemas.
