# Serialization and typed outcomes

Continues `boundary.md` (sections 1-2: conversions, library exchange, validation).

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
  `Field(exclude_if=lambda v: v == 0)`, `computed_field(exclude_if=...)` (v2.13+), or
  call-level `exclude_unset/exclude_none/exclude_defaults`.
- One serializer per field/model; plain and wrap cannot be combined
  (`docs/concepts/serialization.md:227-229@v2.14.1`); `@field_serializer` validates
  field names (v2.13). Prefer `PlainSerializer` inside the `t` alias so the type owns its
  output shape everywhere it is used. Root payloads wrap in `m.RootModel[...]` instead
  of dict contracts.
- `model_dump(mode="json")` yields JSON-compatible Python values; `mode="python"` keeps
  rich objects (`docs/concepts/serialization.md:41-85@v2.14.1`). Library adapters that
  need a mapping use `mode="json"`.
- Aliases: `alias` sets both directions; `validation_alias` (`AliasChoices`,
  `AliasPath`) and `serialization_alias` override it per direction
  (`pydantic/fields.py:1494-1505@v2.14.1`). `populate_by_name` is slated for
  deprecation — use `validate_by_name` / `validate_by_alias` / `serialize_by_alias`
  in the preset (`pydantic/config.py:187-194,1078-1161@v2.14.1`).
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
