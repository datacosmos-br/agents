## 1. Conversions — dict, TypedDict, dataclass, JSON

Parse untrusted input exactly once, at the boundary — JSON always through Pydantic:

```python
model = Shipment.model_validate(payload)  # dict -> model
model = Shipment.model_validate_json(raw)  # JSON -> model (single pass)
model = Shipment.model_validate(dto, from_attributes=True)  # dataclass/ORM -> model
payload = u.model.dump(model)  # model -> JsonMapping
raw = model.model_dump_json(indent=2)  # model -> JSON
```

- Never `Model.model_validate(json.loads(raw))`; the direct JSON entry point parses and
  validates in one pass. The stdlib `json` module never appears at a model boundary —
  `u` owns `from_json`/`to_json`/`to_jsonable_python` for non-model JSON work.
- Non-model types (unions, collections, scalars) validate through cached
  `t.TypeAdapters` factories — module-level, constructed once, the `@classmethod @cache`
  catalog pattern. A local `TypeAdapter(...)` inside a function is a violation (rebuilds
  validators per call).

```python
def handler(raw: str) -> r[t.JsonMapping]:
    return u.model.validate_value(
        t.TypeAdapters.json_mapping_adapter(), raw, from_json=True
    )
```

- `TypedDict` never crosses a public boundary as a contract; if an upstream API hands
  one over, convert at the edge through a `t.*` alias + adapter into a model. Same for
  plain `dict` payloads: they are ingress data, not contracts.
- Stdlib dataclasses and ORM objects convert with `from_attributes=True` (field-level
  `ConfigDict(from_attributes=True)` when the type is always attribute-sourced).
- Round-trip law: validate once on ingress, dump once on egress; never re-validate owned
  data flowing between internal components.

### Library data exchange — every third-party payload enters as a model

Every value a library hands back (YAML, TOML, JSON, pydantic-settings, structlog, HTTP,
LDAP, database drivers) is validated into an `m` model at the one adapter that calls the
library, and every value FLEXT hands to a library leaves through `model_dump` /
`model_dump_json` at that same adapter. Consumers see only models.

| Library output | Ingress | Never |
| --- | --- | --- |
| JSON text/bytes | `Model.model_validate_json(raw)` / `adapter.validate_json(raw)` | `json.loads` then validate |
| `yaml.safe_load(...)` / `tomllib.load(...)` value | `Model.model_validate(loaded)` or a module-level adapter | `cast(...)` or `isinstance` walks on the loaded value |
| ORM / attribute objects | `model_validate(obj, from_attributes=True)` | hand-copying attributes |
| Mapping a library requires back (structlog processor event, pydantic-settings source `_read_file`) | build from `model.model_dump(mode="json")` at the adapter | passing a FLEXT dict contract around |

The mapping a library requires back is that library's contract
(`pydantic_settings/sources/base.py:237-239@v2.15.0`), produced and consumed inside the
adapter; it never becomes a FLEXT type.

### Updating validated data

`model_copy(update=...)` writes the update into `__dict__` without validation and
bypasses `frozen` (`pydantic/main.py:422-468@v2.14.1`). For owned data, build the new
state through validation: `type(model).model_validate(model.model_dump() | update)` at
the owning utility, or construct the new instance directly with typed values.

## 2. Validation practice — centralized owners

- Validators are centralized: reusable constraints live as `t` annotated aliases;
  runtime invariants live in `u`/runtime validation owners (e.g. the UTC enforcer used
  by timestamps); per-field logic uses `u.field_validator`/ `u.model_validator` in the
  model. Copy-pasted validator bodies across models are a violation — promote the logic
  to the `t`/`u` owner.
- Prefer declarative constraints over imperative checks:
  `Field(gt=0, pattern=..., min_length=...)`, `StringConstraints` (v2.13 adds
  `ascii_only`), and reusable aliases declared in `t`:

```python
type MachineId = Annotated[
    str, mp.StringConstraints(pattern=r"^[a-z0-9-]+$", to_lower=True)
]
```

- Validator modes: `after` (default, typed — first choice), `before` (raw input, `Any` —
  normalization only), `wrap` (handler-based — restricted to documented cases; slowest),
  `plain` (replaces validation entirely — forbidden without a documented owner
  justification).
- Ordering: before/wrap run right-to-left, after run left-to-right; field order defines
  when `info.data` is populated — never read a field validated after the current one.
- Validation context replaces globals: pass `Model.model_validate(data, context={...})`
  and read `info.context` in validators; the same exists for serialization.
- Raise `ValueError` (or `PydanticCustomError` for typed errors) inside validators; the
  first exception escapes — never catch to default, coerce, or aggregate.
- Defaults: unvalidated unless `validate_default=True` (strict presets set it).
  `validate_assignment=True` (managed presets) revalidates on attribute assignment;
  frozen presets reject assignment outright.
- Sequences with expensive item validation may use `Annotated[list[T], m.FailFast()]` to
  stop at the first error — an explicit, documented trade-off, not a default.
- Annotated validator order: `before`/`wrap` run right-to-left, then `after`
  left-to-right; decorator validators are appended last
  (`docs/concepts/validators.md:727-747@v2.14.1`). Put the reusable `t` alias first and
  layer field-specific validators on top.
- `info.data` holds only fields declared (and validated) earlier, and is `None` in
  model validators (`docs/concepts/validators.md:631-636@v2.14.1`).
- Model `before` validators receive raw input that is not always a dict; never mutate
  it and then raise — with unions the mutated value reaches the next branch
  (`docs/concepts/validators.md:492-520@v2.14.1`).
- `Annotated[int, Field(...)] | None` applies the `Field` to `int`, not to the field;
  put `= m.Field(...)` on the assignment for defaults, aliases and discriminators
  (`docs/concepts/fields.md:31-97@v2.14.1`). Named `type` aliases may carry
  constraints and JSON metadata only, never `default`/`alias`/`deprecated`
  (`docs/concepts/types.md:305-345@v2.14.1`).
- `validate_call` builds its schema once at decoration and validates every call; it is
  for public entry points that receive untyped input, not internal calls between typed
  components (`pydantic/_internal/_validate_call.py:86-137@v2.14.1`;
  `docs/concepts/validation_decorator.md:410-418@v2.14.1`).
