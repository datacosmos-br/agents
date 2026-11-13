# Serialization and typed outcomes

Continues [boundary.md](boundary.md). The research tags below describe upstream
mechanisms; the selected project owns aliases, exposure and its outward protocol.

## 3. Serialization practice

- Subclass exposure follows the declared payload contract. Where supported at the
  selected floor, model/dataclass polymorphic serialization is narrower than the
  global `serialize_as_any` runtime flag. Preserve the approved field exposure;
  enabling a capability can expose additional subclass fields, not merely speed up
  the same output. See [the native distinction](https://docs.pydantic.dev/latest/concepts/serialization/).

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
- Python and JSON modes have distinct representation contracts. Under the governed
  type-preserving enum policy, Python fields/dumps retain members and JSON emits
  their values. A library requesting a Python mapping does not automatically require
  JSON coercion (`docs/concepts/serialization.md:41-85@v2.14.1`).
- A serializer or `RootModel` can produce a scalar, sequence or other declared output.
  A model annotation or JSON Schema does not prove that a dump is a mapping. Validate
  the actual public outward contract; do not cast or coerce output to fit an assumed
  envelope. Validation-mode and serialization-mode schemas are separate evidence.
- Aliases: `alias` sets both directions; `validation_alias` (`AliasChoices`,
  `AliasPath`) and `serialization_alias` override it per direction
  (`pydantic/fields.py:1494-1505@v2.14.1`). `populate_by_name` is slated for
  deprecation — use `validate_by_name` / `validate_by_alias` / `serialize_by_alias`
  in the preset (`pydantic/config.py:187-194,1078-1161@v2.14.1`).
- Temporal/bytes JSON policy belongs to the selected preset/config owner, not an
  ad-hoc formatter. Verify the effective native options at that floor; a copied
  `ContractModel` name does not prove which serialization settings it carries.

A projected serializable payload retains the original concrete annotation's native
validation and serializers. The projection does not copy their bodies. DI fields have
a different purpose: schema exclusion (for example `SkipJsonSchema`) and dump exclusion
(`Field(exclude=True)`) are independent declarations at their port's existing owner.

## 4. Typing with p and r

- Services and handlers declare outcomes as `p.Result[ModelT]` and construct through the
  railway: `r[ModelT].ok(model)` / `e.fail_validation(...)`.
- The declared result/error boundary converts native validation failure while
  preserving the original cause. Resolve its actual public `u`/`e` capability at the
  selected supplier; a copied helper name is not runtime proof.

- Catching `ValidationError` anywhere else to normalize, default, retry, or aggregate is
  a violation — the first exception escapes with its traceback.
- Models annotate ports: `p` protocols + `r` outcomes + `m` payloads; `t` aliases carry
  reusable annotated types; `Any`/`object`/`dict` never appear as contracts.
