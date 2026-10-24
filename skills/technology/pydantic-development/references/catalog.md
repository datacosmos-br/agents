# Pydantic catalog — capabilities, performance, removal list

Citations: `path:line@v2.14.1` in `pydantic/pydantic`, `@v2.15.0` in
`pydantic/pydantic-settings`. Mechanisms behind each rule: `internals.md`.

## 1. Capability inventory at the 2.14 floor

Use these to the maximum so consumers never re-validate, narrow or convert.

| Capability | Use it for | Reference |
| --- | --- | --- |
| `ConfigDict` presets (`m.*`) | one configuration contract per preset, inherited | `pydantic/config.py:34@v2.14.1` |
| `Field` metadata | constraints, aliases, `discriminator`, `frozen`, `exclude`, `exclude_if`, `default_factory` (may take validated data) | `pydantic/fields.py:1327-1366@v2.14.1`; `_fields.py:844-857` |
| `Annotated` aliases (`type X = Annotated[...]`) in `t` | reusable constraints + validators + serializers; one `$defs` entry | `docs/concepts/types.md:203-260@v2.14.1` |
| `StringConstraints` | strip/case/length/pattern/`ascii_only` on `str` | `pydantic/types.py:699-756@v2.14.1` |
| `AfterValidator` / `BeforeValidator` / `WrapValidator` | reusable validation inside `t` aliases | `pydantic/functional_validators.py:30,91,258@v2.14.1` |
| `field_validator` / `model_validator` (`after` = instance method) | per-model invariants | `functional_validators.py:375-493,735-743@v2.14.1` |
| `PlainSerializer` / `WrapSerializer` / `field_serializer` / `model_serializer` | output shape owned by the type | `pydantic/functional_serializers.py:21,91,224-230,355-361@v2.14.1` |
| `computed_field` | derived read-only values serialized with the model | `pydantic/fields.py:1865-2060@v2.14.1` |
| Discriminated unions (`Field(discriminator=)`, `Discriminator` + `Tag`) | polymorphic payloads, O(1) dispatch, exact narrowing | `docs/concepts/unions.md:18,188-258@v2.14.1` |
| `StrEnum` field types and `Literal[c.X.MEMBER]` tags | closed domains; enum tags work as discriminators | `tests/types/unions/test_discriminated_union.py:406-434@v2.14.1` |
| `InstanceOf[T]` | field typed by a class or `@runtime_checkable` protocol without `arbitrary_types_allowed` | `functional_validators.py:760-817@v2.14.1`; `tests/test_types.py:1861-1886@v2.14.1` |
| `RootModel[T]` | root payloads (lists, scalars) as models | `pydantic/root_model.py:34-118@v2.14.1` |
| Generic models (`BaseModel, Generic[T]`) | parametrized containers, cached per parametrization | `pydantic/_internal/_generics.py:57-144,464-553@v2.14.1` |
| `TypeAdapter` (module-level) | non-model types: unions, collections, scalars | `pydantic/type_adapter.py:160-678@v2.14.1` |
| `model_validate_json` / `TypeAdapter.validate_json` | single-pass JSON ingress in Rust | `docs/concepts/performance.md:8-19@v2.14.1` |
| `model_validate(..., from_attributes=True)` | ORM/dataclass/attribute objects | `pydantic-core/src/input/input_python.rs:513-540@v2.14.1` |
| Validation and serialization `context` | per-call data instead of globals | `docs/concepts/validators.md:638-663@v2.14.1`; `serialization.md:505-533` |
| `polymorphic_serialization` | subclass-aware dumps (models/dataclasses) | `pydantic/config.py:1209@v2.14.1`; `serialization.md:616-644` |
| `SecretStr` / `SecretBytes` | credentials; masked repr/JSON, constant-time compare | `pydantic/types.py:1819-1858@v2.14.1` |
| `FailFast` | stop sequence validation at first error (documented trade-off) | `pydantic/types.py:3370-3403@v2.14.1` |
| `validate_call` | validated public entry points (cost per call, schema built once) | `pydantic/_internal/_validate_call.py:86-137@v2.14.1`; `validation_decorator.md:410-418` |
| `MISSING` sentinel | explicit absence distinct from `None` — import from `pydantic` | `pydantic/experimental/missing_sentinel.py:18-25@v2.14.1` |
| pydantic-settings sources | env/dotenv/secrets/YAML/TOML/JSON/pyproject/CLI with deep merge | `pydantic_settings/__init__.py:5-29@v2.15.0` |

## 2. Performance (upstream guidance, FLEXT reading)

| Upstream rule | FLEXT application | Reference |
| --- | --- | --- |
| `model_validate_json` over `json.loads` + validate | mandatory at every JSON boundary | `performance.md:8-19@v2.14.1` |
| Instantiate `TypeAdapter` once | module-level constant or one cached factory owner; never per call | `performance.md:21-48@v2.14.1`; `type_adapter.md:95-97` |
| Concrete `list`/`tuple`/`dict` over `Sequence`/`Mapping` | model field annotations use concrete containers (`tuple[...]` for frozen data); function parameters keep the abstract protocol | `performance.md:50-56@v2.14.1` |
| Tagged unions over smart unions | every polymorphic field is discriminated | `performance.md:98-138@v2.14.1`; `unions.md:18` |
| Avoid wrap validators | `after` first; `before` only to normalize raw input | `performance.md:183-187@v2.14.1` |
| `TypedDict` instead of nested models | **rejected**: TypedDict is not a FLEXT contract; compress models instead | `performance.md:140-181@v2.14.1` |
| `Any` when no validation is needed | **rejected** for owned data; FLEXT types every field | `performance.md:59-74@v2.14.1` |
| `defer_build` | only at a documented owner for startup latency; never to hide a declaration defect | `pydantic/config.py:798-809@v2.14.1` |
| `cache_strings` (default `all`) | keep the default | `pydantic/config.py:1056-1076@v2.14.1` |
| Frozen over `validate_assignment` | frozen presets for data; managed (assignment-validated) only for genuinely mutable state | `pydantic-core/src/validators/model.rs:184-240@v2.14.1` |

## 3. Experimental features

The `experimental` package and its APIs (pipeline `validate_as`, partial validation
`experimental_allow_partial`, `generate_arguments_schema`) may change or disappear
without notice (`docs/version-policy.md:55,73-77@v2.14.1`;
`docs/concepts/experimental.md:3,15,153@v2.14.1`), and no runtime warning marks their
use (`pydantic/warnings.py:110-114@v2.14.1`). Allowed only inside a documented
flext-core owner with an upgrade note; never in public contracts.

## 4. Removal catalog — banned forms and their replacements

Upstream deprecations (all removed in Pydantic 3, `pydantic/warnings.py:57-103@v2.14.1`)
plus FLEXT law. Each row is enforced by an ast-grep rule applied by `make mod`.

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
| `model_rebuild()` / `_types_namespace` | declaration order and facade exports (`declaration.md` §1) | FLEXT law; `internals.md` §3 |
| `model_construct()` | `model_validate` / constructor | skips validation entirely (`pydantic/main.py:356-408@v2.14.1`) |
| `model_copy(update=...)` on validated data | `type(model).model_validate(model.model_dump() \| update)` at an owner, or a new instance | does not validate and bypasses `frozen` (`pydantic/main.py:422-468@v2.14.1`) |
| `SkipValidation`, `PlainValidator` without owner justification | real validation | stores wrong data silently (`functional_validators.py:834-853@v2.14.1`; `validators.md:801-807`) |
| `OnErrorOmit` | explicit validation failure | drops invalid items silently (`pydantic/types.py:3307-3367@v2.14.1`) |
| `serialize_as_any=True` call flag | `polymorphic_serialization=True` or per-field `SerializeAsAny` | leaks subclass fields globally (`serialization.md:604-644@v2.14.1`) |
| `arbitrary_types_allowed=True` on general presets | `InstanceOf[p.X]` (`t.Port[...]`) per field | turns every unknown class into an unchecked `isinstance` (`_generate_schema.py:738-748@v2.14.1`) |
| `extra="allow"` on owned contracts | declared fields; `extra="forbid"` presets | unknown keys silently stored in `__pydantic_extra__` |
| `model_config = {...}` raw dict | `ConfigDict(...)` via a preset | typed config |
| Custom `__eq__` / `__hash__` on value models | `frozen=True` preset | generated correctly (`_model_construction.py:261-262,512-525@v2.14.1`) |
| `__init__` override on a model | validators, `default_factory`, `model_post_init` | bypasses the validator contract (`pydantic/main.py:280-287@v2.14.1`) |
| `TypeAdapter(...)` inside a function | module-level adapter / cached factory owner | rebuilt per call (`type_adapter.py:208-294@v2.14.1`) |
| `json.loads` / `yaml.safe_load` / `tomllib` result fed to `cast(...)` or `isinstance` checks | `model_validate_json`, or `model_validate` / adapter on the loaded value | one validated boundary |
| `model_dump()` followed by key indexing or dict surgery | attribute access, `computed_field`, serializers | the model already holds typed values |
| `Model.model_validate({...})` built from local variables | `Model(field=value, ...)` | extra dict round-trip |
| `isinstance(x, (dict, Mapping))` on owned payloads | typed model fields / discriminated unions | narrowing belongs to validation |
| Behavior methods on declaration-layer models | `u` utilities / services | declaration layers stay data-only |
| String `Literal[...]` closed domains and magic strings | `StrEnum` in `c`, used as the field type | one constant owner |
| `Optional[T]`, `Any`, `object`, bare `dict` on model fields | `T \| None`, `t.*` aliases, `p.*` protocols via `InstanceOf` | precise contracts |
| `TypedDict` / `dataclass` / `NamedTuple` as data contracts | `m` model | FLEXT contract law |
| `with_config(config=...)` keyword, `Examples({dict})`, `MISSING` from `experimental` | positional config, list examples, `from pydantic import MISSING` | `config.py:1268-1271`; `json_schema.py:3084-3089`; `missing_sentinel.py:18-25@v2.14.1` |

pydantic-settings: `read_env_file()` is deprecated in favor of
`DotEnvSettingsSource._static_read_env_file` (`sources/providers/dotenv.py:189-203@v2.15.0`);
FLEXT consumes settings only through its `settings` facade, never through source
internals.

## 5. Evidence and gates

Diagnostics, generation, repair, formatting, checks and tests run only through the
root Make verbs. Before tests, exercise the real runtime path (import the facade,
validate a representative payload from a neutral directory). Every catalog row maps to
an ast-grep rule with fixtures under flext-infra; `make mod` applies the rewrites and
`make check` fails on any remaining finding.
