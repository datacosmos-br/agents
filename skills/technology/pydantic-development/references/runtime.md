# Pydantic runtime internals — validation, equality, adapters, settings

Continues [internals.md](internals.md). These are versioned implementation notes,
not a project dependency declaration, latency promise or replacement for the selected
model's public contract.

## 5. Validation runtime (pydantic-core)

- The native JSON validator can parse and validate directly in the core runtime
  (`pydantic-core/src/validators/mod.rs:471-500@v2.14.1`;
  `validators/model_fields.rs:146-156`). Python callbacks may still receive Python
  objects. Use the direct JSON boundary and measure the actual path rather than
  claiming that every schema avoids allocation or is universally faster.
- Strict mode is resolved per schema, then config, default lax
  (`pydantic-core/src/build_tools.rs:44-47@v2.14.1`); in JSON, strings convert to
  numbers or booleans only when not strict (`input/input_json.rs:152,171,191@v2.14.1`).
- String caching (`cache_strings`, default all) interns repeated strings
  (`pydantic-core/src/tools.rs:141-143@v2.14.1`).
- The default instance policy can reuse an instance of the expected class
  (`validators/model.rs:174-175@v2.14.1`). That is not a zero-cost guarantee or proof
  that changed mutable state remains valid. Reuse admitted values under the same
  trust state; a changed boundary follows the owner's native revalidation policy.
- `validate_assignment` copies `__dict__` twice and revalidates the field on every
  assignment (`validators/model.rs:184-240@v2.14.1`,
  `validators/model_fields.rs:220-243@v2.14.1`). Frozen models avoid the cost entirely.
- Frozen enforcement includes Python `_check_frozen` (`pydantic/main.py:96-100@v2.14.1`)
  and Rust `FrozenInstance`/`FrozenField` (`validators/model.rs:192-193@v2.14.1`).

Neither shallow nor deep copying validates an update. Frozen and assignment policies
do not monitor every mutation inside nested containers. Preserve the declared data
and collection contracts; see [changed trust state](boundary.md#updating-validated-data)
and the [native instance policy](https://docs.pydantic.dev/latest/concepts/models/).

## 6. Native equality and hashing

- `BaseModel.__eq__` compares generic origin, private and extra attributes, and field
  values (`pydantic/main.py:1225-1282@v2.14.1`).
- `frozen=True` generates `__hash__` over field values unless the class defines one
  (`_model_construction.py:261-262,512-525@v2.14.1`), regenerated for frozen subclasses.

The current FLEXT contract preserves native model-value equality and compares entity
identity explicitly by id. Do not restore an identity-based equality/hash override.
A frozen model can still contain unhashable or mutable values; choose hashable
collections only when the domain requires them. See [identity contracts](composition.md#5-identity-models--id-timestamps-version).

## 7. TypeAdapter has no cache by type

- `TypeAdapter.__init__` builds a fresh validator and serializer unless the type
  already carries complete pydantic attributes (`pydantic/type_adapter.py:208-294@v2.14.1`);
  there is no type-keyed cache in the module.
- Upstream instruction: create the adapter once and reuse it
  (`docs/concepts/type_adapter.md:95-97@v2.14.1`, `docs/concepts/performance.md:21-48@v2.14.1`).

Reuse the existing native `u` adapter owner. Do not add a consumer cache or assume
that a `t.TypeAdapter` annotation is a constructor. Profile repeated construction
against reuse at the selected floor before making a cost claim.

## 8. pydantic-settings source pipeline

The [settings procedure](procedure.md#4-pydantic-settings) owns source selection and
FLEXT admission. The citations below explain that selected implementation:

- Sources are called in priority order and deep-merged with `deep_update` so a lower
  source can still fill missing nested keys (`pydantic_settings/main.py:485-507@v2.15.0`;
  `pydantic/_internal/_utils.py:131-139@v2.14.1`).
- Default priority: init kwargs, environment, dotenv, secrets dir, then field
  defaults; CLI first when enabled (`docs/index.md:3096-3106@v2.15.0`).
- `BaseSettings` defaults: `extra='forbid'`, `validate_default=True`,
  `arbitrary_types_allowed=True` (`pydantic_settings/main.py:617-656@v2.15.0`).
- A custom file source implements `_read_file(path) -> dict[str, Any]`; the parsed
  mapping is handed to `InitSettingsSource` and validated by the settings model
  (`pydantic_settings/sources/base.py:215-239@v2.15.0`,
  `sources/providers/json.py:42-47@v2.15.0`). The mapping is the library's contract,
  not a FLEXT contract: it is produced and consumed inside the source and never
  escapes it.
