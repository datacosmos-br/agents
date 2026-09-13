## 1. Conversions — dict, TypedDict, dataclass, JSON

Parse untrusted input exactly once, at the boundary — JSON always through
Pydantic:

```python
model = Shipment.model_validate(payload)  # dict -> model
model = Shipment.model_validate_json(raw)  # JSON -> model (single pass)
model = Shipment.model_validate(dto, from_attributes=True)  # dataclass/ORM -> model
payload = u.model.dump(model)  # model -> JsonMapping
raw = model.model_dump_json(indent=2)  # model -> JSON
```

- Never `Model.model_validate(json.loads(raw))`; the direct JSON entry point
  parses and validates in one pass. The stdlib `json` module never appears at
  a model boundary — `u` owns `from_json`/`to_json`/`to_jsonable_python` for
  non-model JSON work.
- Non-model types (unions, collections, scalars) validate through cached
  `t.TypeAdapters` factories — module-level, constructed once, the
  `@classmethod @cache` catalog pattern. A local `TypeAdapter(...)` inside a
  function is a violation (rebuilds validators per call).

```python
def handler(raw: str) -> r[t.JsonMapping]:
    return u.model.validate_value(
        t.TypeAdapters.json_mapping_adapter(), raw, from_json=True
    )
```

- `TypedDict` never crosses a public boundary as a contract; if an upstream
  API hands one over, convert at the edge through a `t.*` alias + adapter into
  a model. Same for plain `dict` payloads: they are ingress data, not
  contracts.
- Stdlib dataclasses and ORM objects convert with `from_attributes=True`
  (field-level `ConfigDict(from_attributes=True)` when the type is always
  attribute-sourced).
- Round-trip law: validate once on ingress, dump once on egress; never
  re-validate owned data flowing between internal components.

## 2. Validation practice — centralized owners

- Validators are centralized: reusable constraints live as `t` annotated
  aliases; runtime invariants live in `u`/runtime validation owners (e.g. the
  UTC enforcer used by timestamps); per-field logic uses `u.field_validator`/
  `u.model_validator` in the model. Copy-pasted validator bodies across models
  are a violation — promote the logic to the `t`/`u` owner.
- Prefer declarative constraints over imperative checks: `Field(gt=0,
  pattern=..., min_length=...)`, `StringConstraints` (v2.13 adds
  `ascii_only`), and reusable aliases declared in `t`:

```python
type MachineId = Annotated[
    str, mp.StringConstraints(pattern=r"^[a-z0-9-]+$", to_lower=True)
]
```

- Validator modes: `after` (default, typed — first choice), `before` (raw
  input, `Any` — normalization only), `wrap` (handler-based — restricted to
  documented cases; slowest), `plain` (replaces validation entirely —
  forbidden without a documented owner justification).
- Ordering: before/wrap run right-to-left, after run left-to-right; field
  order defines when `info.data` is populated — never read a field validated
  after the current one.
- Validation context replaces globals: pass `Model.model_validate(data,
  context={...})` and read `info.context` in validators; the same exists for
  serialization.
- Raise `ValueError` (or `PydanticCustomError` for typed errors) inside
  validators; the first exception escapes — never catch to default, coerce,
  or aggregate.
- Defaults: unvalidated unless `validate_default=True` (strict presets set
  it). `validate_assignment=True` (managed presets) revalidates on attribute
  assignment; frozen presets reject assignment outright.
- Sequences with expensive item validation may use `Annotated[list[T],
  m.FailFast()]` to stop at the first error — an explicit, documented
  trade-off, not a default.

## 3. Serialization practice

- Subclass exposure uses `polymorphic_serialization` (v2.13+), not the global
  duck-typing flag:

```python
outer.model_dump(polymorphic_serialization=True)  # ok — models/dataclasses
outer.model_dump(serialize_as_any=True)  # forbidden — applies to every value
```

  Per-field duck typing, when the contract genuinely requires it, uses
  `SerializeAsAny[User]` on that field only.
- Conditional exclusion is declarative: `Field(exclude=True)`,
  `Field(exclude_if=lambda v: v == 0)`, `computed_field(exclude_if=...)`
  (v2.13+), or call-level `exclude_unset/exclude_none/exclude_defaults`.
- One serializer per field/model; `@field_serializer` validates field names
  (v2.13). Root payloads wrap in `m.RootModel[...]` instead of dict contracts.
- Temporal/bytes JSON shapes come from constants/config (`ser_json_timedelta`,
  `ser_json_bytes` — already set by `ContractModel`), never ad-hoc string
  formatting in serializers.

## 4. Typing with p and r

- Services and handlers declare outcomes as `p.Result[ModelT]` and construct
  through the railway: `r[ModelT].ok(model)` / `e.fail_validation(...)`.
- The only authorized `ValidationError` conversion point is the result
  boundary (`u.model.validate_value`, `e.fail_validation`), which catches the
  constant `c.EXC_ATTR_RUNTIME_VALIDATION` and preserves the cause:

```python
def parse(raw: str) -> p.Result[Shipment]:
    return u.model.validate_value(Shipment, raw, from_json=True)
```

- Catching `ValidationError` anywhere else to normalize, default, retry, or
  aggregate is a violation — the first exception escapes with its traceback.
- Models annotate ports: `p` protocols + `r` outcomes + `m` payloads; `t`
  aliases carry reusable annotated types; `Any`/`object`/`dict` never appear
  as contracts.
