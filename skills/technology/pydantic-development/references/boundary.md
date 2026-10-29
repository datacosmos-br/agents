## 1. Conversions — dict, TypedDict, dataclass, JSON

Parse untrusted input exactly once, at the boundary — JSON always through Pydantic:

```python
model = Shipment.model_validate(payload)  # dict -> model
model = Shipment.model_validate_json(raw)  # JSON -> model (single pass)
model = Shipment.model_validate(dto, from_attributes=True)  # dataclass/ORM -> model
payload = u.model.dump(model)  # model -> JsonMapping
raw = model.model_dump_json(indent=2)  # model -> JSON
```

- Never `Model.model_validate(json.loads(raw))`; use the native JSON validation
  entry point. Non-model JSON work uses the selected public `u` owner, not a
  copied parser or an assumed helper name.
- Non-model types (unions, collections, scalars) validate through the selected
  owner's reusable adapter. Runtime construction belongs to `u`; `t.TypeAdapter[T]`
  is an annotation, not a callable factory. Do not recreate an adapter per item,
  invent a `t.TypeAdapters` catalog, or add a consumer cache beside its owner.

- `TypedDict` never crosses a public boundary as a contract; if an upstream API hands
  one over, convert at the edge through a `t.*` alias + adapter into a model. Same for
  plain `dict` payloads: they are ingress data, not contracts.
- Attribute-sourced dataclass/ORM inputs use `from_attributes=True` at their declared
  boundary; a shared model policy belongs to its preset, not a consumer `ConfigDict`.
- Validate new external data once and pass admitted models by reference. A changed
  trust boundary still needs its declared validation; an earlier parse is not proof
  that a mutable instance remains valid. `model_validate(existing_model)` normally
  reuses the instance without revalidation. Where required, select native
  `revalidate_instances` at the model owner and test nested instances and subclasses;
  never dump to a dict or JSON merely to force another admission.

## 2. Validation practice — centralized owners

- Reusable constraints live as `t` annotations. Native field/model validators
  belong to the declaring model through its `m` Pydantic surface. Reusable
  algorithms remain with their approved `u` owner; models do not discover
  services or perform I/O. Respect the selected family's import boundary
  rather than importing its unfinished own utility facade.
- Prefer declarative constraints over imperative checks:
  `Field(gt=0, pattern=..., min_length=...)`, `StringConstraints` (v2.13 adds
  `ascii_only`), and reusable aliases declared in `t`. Use only capabilities
  present at the selected dependency floor and exposed by its public facade.

- Validator modes: prefer typed `after` invariants; use `before` only for the declared
  raw ingress shape, without loose public contracts. A required `wrap` delegates to
  the native handler; profile its cost rather than assuming a universal ranking.
  `plain` replaces validation, so its owner must prove the complete positive/negative
  contract; it never authorizes accepting invalid data or returning a default.
- Ordering: before/wrap run right-to-left, after run left-to-right; field order defines
  when `info.data` is populated — never read a field validated after the current one.
- Validators are data invariants, not effect hooks: nested generic validation may run
  a model validator again. Keep them free of I/O and externally visible side effects.
  A `computed_field` exposes derived output; it does not validate an input field.
- Explicit validation context can carry boundary facts through `info.context`;
  it is not a service locator or a reason to read process globals. The same
  distinction applies to serialization context.
- Raise `ValueError` or the exported native custom-error type for data invariants.
  Pydantic packages those failures as `ValidationError`; preserve that native result
  and cause at the declared error boundary. Programming errors are not input
  normalization opportunities. Never recover with a default or retry.
- Defaults: unvalidated unless `validate_default=True` (strict presets set it).
  `validate_assignment=True` (managed presets) revalidates on attribute assignment;
  frozen presets reject assignment outright.
- Assignment validation does not intercept every in-place mutation of a nested
  collection, and frozen models are not recursively immutable. Select the native
  collection contract at its owner. `model_copy(update=...)` does not validate
  updates; it cannot replace admission of changed external data.
- Sequences with expensive item validation may use `Annotated[list[T], m.FailFast()]` to
  stop at the first error — an explicit, documented trade-off, not a default.

These contracts follow [validators](https://github.com/pydantic/pydantic/blob/v2.14.1/docs/concepts/validators.md)
and [instance revalidation](https://github.com/pydantic/pydantic/blob/v2.14.1/pydantic/config.py)
at v2.14.1. They are not permission to weaken the project's presets.

## 3. Serialization practice

- Subclass exposure uses `polymorphic_serialization` (v2.13+), not the global
  duck-typing flag:

```python
outer.model_dump(polymorphic_serialization=True)  # ok — models/dataclasses
outer.model_dump(serialize_as_any=True)  # forbidden — applies to every value
```

Per-field duck typing, when the contract genuinely requires it, uses
`SerializeAsAny[User]` on that field only.

Python dumps and JSON dumps have different output contracts. Under the selected
type-preserving enum policy, Python fields/dumps retain enum members while the
JSON boundary emits their values. A structural payload projection delegates both
directions to its original concrete annotation; it does not copy serializers.
The schema's validation and serialization modes are checked independently.
For DI fields, `SkipJsonSchema` excludes schema exposure and `Field(exclude=True)`
excludes dumps; neither marker implies the other. Keep those declarations at the
port's existing owner instead of treating a runtime object as a payload.

- Conditional exclusion is declarative: `Field(exclude=True)`,
  `Field(exclude_if=lambda v: v == 0)`, `computed_field(exclude_if=...)` (v2.13+), or
  call-level `exclude_unset/exclude_none/exclude_defaults`.
- One serializer per field/model; `@field_serializer` validates field names (v2.13).
  Root payloads wrap in `m.RootModel[...]` instead of dict contracts.
- Temporal/bytes JSON shapes come from constants/config (`ser_json_timedelta`,
  `ser_json_bytes` — already set by `ContractModel`), never ad-hoc string formatting in
  serializers.

## 4. Typing with p and r

- Services and handlers declare outcomes as `p.Result[ModelT]` and construct through the
  railway: `r[ModelT].ok(model)` / `e.fail_validation(...)`.
- The only authorized `ValidationError` conversion point is the result boundary
  (`u.model.validate_value`, `e.fail_validation`), which catches the constant
  `c.EXC_ATTR_RUNTIME_VALIDATION` and preserves the cause:

```python
def parse(raw: str) -> p.Result[Shipment]:
    return u.model.validate_value(Shipment, raw, from_json=True)
```

- Catching `ValidationError` anywhere else to normalize, default, retry, or aggregate is
  a violation — the first exception escapes with its traceback.
- Models annotate ports: `p` protocols + `r` outcomes + `m` payloads; `t` aliases carry
  reusable annotated types; `Any`/`object`/`dict` never appear as contracts.
