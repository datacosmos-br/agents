# Pydantic internals — why the practices make consumer code lighter

Source of truth: the pinned upstream source, not memory. Citations are
`path:line@tag` against `github.com/pydantic/pydantic` tag `v2.14.1` (pydantic-core
2.50.1 is vendored in the same tag under `pydantic-core/`) and
`github.com/pydantic/pydantic-settings` tag `v2.15.0`. Re-verify every citation when
the project's declared floor moves.

## 1. Architecture: Python defines, Rust validates and serializes

- Model definition (fields, config, decorators, private attributes) lives in Python;
  validation and serialization live in pydantic-core (Rust). The two communicate only
  through the *core schema*, a typed dict with a `type` key, stored on the class as
  `__pydantic_core_schema__` (`docs/internals/architecture.md:4-48@v2.14.1`).
- Only the fixed core-schema set is supported; there are no custom schema types
  (`docs/internals/architecture.md:39-45@v2.14.1`).
- Serialization rules travel inside the same schema under `serialization`; JSON
  Schema is derived from the core schema (`docs/internals/architecture.md:81-131@v2.14.1`).

Consequence for FLEXT: every rule expressed as a type, constraint, validator or
serializer is compiled once per class into Rust. A rule re-implemented in a consumer
(`isinstance`, `cast`, manual conversion) runs in Python on every call and duplicates
a guarantee the model already gives.

## 2. Class creation pipeline and its cost

At class creation `ModelMetaclass.__new__` (`pydantic/_internal/_model_construction.py`):

1. Captures the defining frame's locals as a weak-valued snapshot
   (`:209-210`, `:780-797@v2.14.1`).
2. Collects fields from the reversed MRO with lenient annotation evaluation
   (`pydantic/_internal/_typing_extra.py:235-291@v2.14.1`).
3. Unless `defer_build`, calls `complete_model_class` (`:248-259@v2.14.1`), which
   generates the core schema through the single `GenerateSchema` entry point
   (`pydantic/_internal/_generate_schema.py:356@v2.14.1`), cleans it (Rust gather,
   inlining of single-use refs, `_generate_schema.py:2847-2911@v2.14.1`), then builds
   `__pydantic_validator__` and `__pydantic_serializer__`
   (`_model_construction.py:621-675@v2.14.1`).
4. Sets `__pydantic_complete__ = True` and calls the `__pydantic_on_complete__` hook
   (`_model_construction.py:677-680@v2.14.1`; `pydantic/main.py:956-965@v2.14.1`).

Reuse already built in:

- Within one build, repeated types collapse to `definition-ref` schemas
  (`_generate_schema.py:2776-2845@v2.14.1`).
- A nested complete model reuses its stored schema (`_generate_schema.py:839-856@v2.14.1`)
  and its prebuilt Rust validator/serializer (`pydantic-core/src/common/prebuilt.rs:7-43@v2.14.1`).
- PEP 695 `type` aliases become one named definition per build, keyed by alias
  identity (`_generate_schema.py:1390-1408@v2.14.1`).

Consequence: fewer, composed models and named `type` aliases cost less to build and
produce smaller schemas than many near-duplicate models.

## 3. Forward references, mocks and why `model_rebuild` appears

- Field evaluation is lenient: an unresolved name marks the field incomplete
  (`pydantic/_internal/_fields.py:474-476,509-510@v2.14.1`).
- An incomplete class gets `MockCoreSchema`/`MockValSer` placeholders
  (`pydantic/_internal/_mock_val_ser.py:156-194@v2.14.1`). Any first use triggers an
  automatic `model_rebuild(_parent_namespace_depth=5)`; failure raises
  `class-not-fully-defined` (`_mock_val_ser.py:96-105@v2.14.1`).
- Resolution namespace: module globals of the class's module, then locals in
  priority order — parent-frame snapshot, the outermost type being built, PEP 695
  type params, the class `__dict__`, and `{ClassName: cls}` so self-references always
  resolve (`pydantic/_internal/_namespace_utils.py:238-287@v2.14.1`).
- The parent snapshot is taken at definition; names bound later are never visible
  through it (`docs/internals/resolving_annotations.md:136-140@v2.14.1`).

The FLEXT failure mode: models nested as inner classes of a facade namespace class.
While the outer class body executes, the outer name is not yet bound in module
globals, and a later sibling is not yet in the body snapshot. An inner model that
references a *later* sibling becomes a mock, and its first standalone use cannot
resolve the bare sibling name — hence the historical `model_rebuild` calls. The cure
is declaration order, not rebuild (see `declaration.md` §1).

## 4. Configuration merge is shallow and follows `bases` order

`ConfigWrapper.for_model` (`pydantic/_internal/_config.py:148-189@v2.14.1`):

- Copies each base's `model_config` in **`bases` order, not MRO**; a later base
  overrides an earlier one (`docs/concepts/config.md:181-183@v2.14.1`).
- Then applies the class body `model_config`, then class keyword arguments (highest).
- The merge is key-by-key `dict.update`: nested values such as `json_schema_extra`
  are replaced, never deep-merged.
- Config does not propagate into nested models; each model is its own boundary
  (`docs/concepts/config.md:207-261@v2.14.1`).

Consequence: preset inheritance is the compression mechanism — one preset per
configuration contract, subclasses add only fields.

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
