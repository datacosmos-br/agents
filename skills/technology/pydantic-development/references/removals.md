# Pydantic removal catalog — banned forms and their replacements

Citations: `path:line@v2.14.1` in `pydantic/pydantic`, `@v2.15.0` in
`pydantic/pydantic-settings`. Capabilities to use instead: `catalog.md`.

This table combines versioned upstream deprecation research with the project's
Pydantic boundary law. Verify availability and deprecation at the selected floor;
the cited tag is not a workspace pin. A claimed automatic cure must identify the
actual native rule, fixtures and consumer proof. The table alone does not establish
that every row already has implemented enforcement.

| Banned | Replacement | Reason / reference |
| --- | --- | --- |
| `import pydantic` / `pydantic_settings` / `pydantic_core` outside flext-core | `m`/`t`/`p`/`u` facades | FLEXT facade law |
| `pydantic.v1`, `pydantic.deprecated.*` | v2 API | `pydantic/v1/__init__.py:1-16`; `_generate_schema.py:1029-1033@v2.14.1` |
| `.dict()`, `.json()`, `parse_obj`, `parse_raw`, `parse_file`, `from_orm`, `construct`, `copy`, `schema`, `schema_json`, `validate`, `update_forward_refs`, `__fields__`, `__fields_set__` | `model_dump`, `model_dump_json`, `model_validate`, `model_validate_json`, `from_attributes=True`, `model_copy`, `model_json_schema`, `model_fields` | `pydantic/main.py:1360-1755@v2.14.1` |
| `@validator`, `@root_validator`, `validate_arguments`, `parse_obj_as`, `schema_of` | `field_validator`, `model_validator`, `validate_call`, `TypeAdapter` | `deprecated/class_validators.py:17-203`; `deprecated/decorator.py:39-48`; `deprecated/tools.py:27-99@v2.14.1` |
| `@model_validator(mode="after")` on a classmethod | instance method returning `self` | `functional_validators.py:735-743@v2.14.1` |
| `class Config`, `BaseConfig`, `Extra`, V1 config keys, `json_encoders`, `schema_generator` | `ConfigDict` presets, serializers | `_internal/_config.py:26,347-408@v2.14.1`; `_generate_schema.py:300-303` |
| `Field(min_items/max_items/allow_mutation/include/regex/const/unique_items/**extra)` | `min_length`/`max_length`/`frozen`/`exclude`/`pattern`/`Literal`/`set`/`json_schema_extra` | `pydantic/fields.py:1435-1513@v2.14.1` |
| `conint`, `confloat`, `constr`, `condecimal`, `conbytes`, `conlist`, `conset`, `confrozenset`, `condate` | `Annotated[..., Field(...)]` / `StringConstraints` aliases in `t` | `pydantic/types.py:167-174,428-433,771-778,1066-1071@v2.14.1` |
| Instance access to `model_fields` / `model_computed_fields` | class access | `pydantic/main.py:292-312@v2.14.1` |
| `Final` field with a default | `ClassVar[...]` | `_internal/_fields.py:511-521@v2.14.1` |
| `model_rebuild()` / `_types_namespace` as declaration repair | complete-import diagnosis and the proven namespace/export owner (`declaration.md` §1) | runtime class identity and supported local scopes are preserved |
| `model_construct()` | `model_validate` / constructor | skips validation entirely (`pydantic/main.py:356-408@v2.14.1`) |
| `model_copy(update=...)` on validated data | construct the new typed state through its validation owner | copying is not revalidation; no dump/mapping-surgery/reparse prescription (`pydantic/main.py:422-468@v2.14.1`) |
| `SkipValidation`, `PlainValidator` without owner justification | real validation | stores wrong data silently (`functional_validators.py:834-853@v2.14.1`; `validators.md:801-807`) |
| `OnErrorOmit` | explicit validation failure | drops invalid items silently (`pydantic/types.py:3307-3367@v2.14.1`) |
| `serialize_as_any=True` call flag | `polymorphic_serialization=True` or per-field `SerializeAsAny` | leaks subclass fields globally (`serialization.md:604-644@v2.14.1`) |
| `arbitrary_types_allowed=True` on general presets | `InstanceOf[p.X]` (`t.Port[...]`) per field | turns every unknown class into an unchecked `isinstance` (`_generate_schema.py:738-748@v2.14.1`) |
| `extra="allow"` on owned contracts | declared fields; `extra="forbid"` presets | unknown keys silently stored in `__pydantic_extra__` |
| `model_config = {...}` raw dict | `ConfigDict(...)` via a preset | typed config |
| Custom `__eq__` / `__hash__` on value models | `frozen=True` preset | generated correctly (`_model_construction.py:261-262,512-525@v2.14.1`) |
| `__init__` used to replace model admission | native validators, `default_factory`, approved lifecycle hooks | preserve the selected framework owner's construction and signature contract |
| `TypeAdapter(...)` recreated per operation | reuse the existing native `u` adapter owner | no second cache or consumer factory (`type_adapter.py:208-294@v2.14.1`) |
| `json.loads` / `yaml.safe_load` / `tomllib` result fed to `cast(...)` or `isinstance` checks | `model_validate_json`, or `model_validate` / adapter on the loaded value | one validated boundary |
| `model_dump()` followed by key indexing or dict surgery | attribute access, `computed_field`, serializers | the model already holds typed values |
| `Model.model_validate({...})` built from local variables | `Model(field=value, ...)` | extra dict round-trip |
| `isinstance(x, (dict, Mapping))` on owned payloads | typed model fields / discriminated unions | narrowing belongs to validation |
| Behavior methods on declaration-layer models | `u` utilities / services | declaration layers stay data-only |
| Copied config/settings policy or values in leaf modules or `c` | one composition-root selection and explicit injection | the original source keeps authority |
| Duplicate validator algorithms | reusable `t` metadata or the approved shared `u` owner registered through `m` | no per-consumer parsing or second validator registry |
| Private-module imports in tests, scripts or examples | public declaring facade and canonical test fixtures | those trees are not alternate APIs |
| An exhaustive `Literal[...]` mirror of a complete string-enum domain | its existing `c` `StrEnum` | proper subsets and discriminator literals remain narrow contracts |
| `Optional[T]`, `Any`, `object`, bare `dict` on model fields | `T \| None`, `t.*` aliases, `p.*` protocols via `InstanceOf` | precise contracts |
| `TypedDict` / `dataclass` / `NamedTuple` as data contracts | `m` model | FLEXT contract law |
| Retired `with_config`/`Examples` forms or an unqualified experimental import | the selected version's public facade and native argument contract | versioned discovery: `config.py:1268-1271`; `json_schema.py:3084-3089`; `missing_sentinel.py:18-25@v2.14.1` |

pydantic-settings: `read_env_file()` is deprecated in favor of
`DotEnvSettingsSource._static_read_env_file` (`sources/providers/dotenv.py:189-203@v2.15.0`);
FLEXT consumes settings only through its `settings` facade, never through source
internals.

