# Pydantic runtime internals — validation, equality, adapters, settings

Continues `internals.md` (sections 1-4: architecture, class creation, forward
references, config merge). Same citation convention.

## 5. Validation runtime (pydantic-core)

- JSON input is parsed by `jiter` straight into a `JsonValue` and validated without
  building a Python dict (`pydantic-core/src/validators/mod.rs:471-500@v2.14.1`); model
  fields iterate the JSON object directly (`validators/model_fields.rs:146-156@v2.14.1`).
  This is why `model_validate_json` beats `model_validate(json.loads(...))`.
- Strict mode is resolved per schema, then config, default lax
  (`pydantic-core/src/build_tools.rs:44-47@v2.14.1`); in JSON, strings convert to
  numbers or booleans only when not strict (`input/input_json.rs:152,171,191@v2.14.1`).
- String caching (`cache_strings`, default all) interns repeated strings
  (`pydantic-core/src/tools.rs:141-143@v2.14.1`).
- `revalidate_instances` defaults to `never`: an instance of the exact class is
  returned as-is (`validators/model.rs:174-175@v2.14.1`). Passing a model object
  where a model is expected therefore costs nothing — reuse the object, never dump and
  re-validate it.
- `validate_assignment` copies `__dict__` twice and revalidates the field on every
  assignment (`validators/model.rs:184-240@v2.14.1`,
  `validators/model_fields.rs:220-243@v2.14.1`). Frozen models avoid the cost entirely.
- Frozen enforcement is double: Python `_check_frozen` (`pydantic/main.py:96-100@v2.14.1`)
  and Rust `FrozenInstance`/`FrozenField` (`validators/model.rs:192-193@v2.14.1`).

## 6. Equality and hashing are already correct

- `BaseModel.__eq__` compares generic origin, private and extra attributes, and field
  values (`pydantic/main.py:1225-1282@v2.14.1`).
- `frozen=True` generates `__hash__` over field values unless the class defines one
  (`_model_construction.py:261-262,512-525@v2.14.1`), regenerated for frozen subclasses.

Consequence: a custom `__eq__`/`__hash__` on a value model is never needed; make the
model frozen and use hashable field types (`tuple`, `frozenset`).

## 7. TypeAdapter has no cache by type

- `TypeAdapter.__init__` builds a fresh validator and serializer unless the type
  already carries complete pydantic attributes (`pydantic/type_adapter.py:208-294@v2.14.1`);
  there is no type-keyed cache in the module.
- Upstream instruction: create the adapter once and reuse it
  (`docs/concepts/type_adapter.md:95-97@v2.14.1`, `docs/concepts/performance.md:21-48@v2.14.1`).

Consequence: `TypeAdapter(list[int])` inside a function rebuilds a Rust validator on
every call. Adapters are module-level constants or cached factories at one owner.

## 8. pydantic-settings source pipeline

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
