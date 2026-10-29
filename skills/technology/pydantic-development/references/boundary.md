## 1. Conversions — dict, TypedDict, dataclass, JSON

Parse untrusted input exactly once, at the boundary — JSON always through Pydantic:

Use the originating model's native Python validator for Python values and its JSON
validator for raw JSON. Attribute-sourced inputs use the declared `from_attributes`
boundary. Output uses that model's native serializer in the mode required by the
outward protocol; do not assume that every dump returns a mapping.

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

### Library data exchange — every third-party payload enters as a model

An owned payload returned by a library is admitted at the adapter that calls it.
The adapter uses the library's native representation at its outward boundary; the
domain receives the owning validated contract. Runtime collaborators and library-local
mappings do not become another payload model or a public FLEXT mapping contract.

| Library output | Ingress | Never |
| --- | --- | --- |
| JSON text/bytes | `Model.model_validate_json(raw)` / `adapter.validate_json(raw)` | `json.loads` then validate |
| Captured YAML/TOML document | the existing `u.Cli.config_decode` source grammar and owning model | `strict=False`, JSON readmission or consumer-side field conversion |
| ORM / attribute objects | `model_validate(obj, from_attributes=True)` | hand-copying attributes |
| Mapping required by a library (processor event or settings source) | its declared native representation inside the adapter; select the owning payload's dump mode when serialization applies | promoting a library-local mapping to a FLEXT contract or forcing JSON coercion |

Select Python or JSON serialization according to that outward contract. A Python
mapping accepted by a library does not automatically require JSON-mode coercion.
The mapping a library requires back is that library's contract
(`pydantic_settings/sources/base.py:237-239@v2.15.0`), produced and consumed inside the
adapter; it never becomes a FLEXT type.

### Updating validated data

`model_copy(update=...)` does not validate its update and cannot replace admission of
changed data (`pydantic/main.py:422-468@v2.14.1`). Construct the new state at its owner
with the declared typed values and native validation. Do not prescribe a model dump,
mapping surgery and reparse as a universal update mechanism.

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

Additional versioned validation details:

- `info.data` contains only earlier validated fields and is `None` for model
  validators (`docs/concepts/validators.md:631-636@v2.14.1`).
- A model `before` validator may receive a non-mapping value. Do not mutate input
  and then raise: a union may pass the changed object to another branch
  (`docs/concepts/validators.md:492-520@v2.14.1`).
- Field-wide defaults, aliases and discriminators belong on their declaring field;
  reusable aliases retain constraints and appropriate metadata. Verify how `Annotated`
  placement affects constructor synthesis at the selected floor
  (`docs/concepts/fields.md:31-97@v2.14.1`; `types.md:305-345`).
- `validate_call` owns repeated validation at an explicitly untyped public boundary;
  it is not required between already typed internal components
  (`docs/concepts/validation_decorator.md:410-418@v2.14.1`).

These contracts follow [validators](https://github.com/pydantic/pydantic/blob/v2.14.1/docs/concepts/validators.md)
and [instance revalidation](https://github.com/pydantic/pydantic/blob/v2.14.1/pydantic/config.py)
at v2.14.1. They are not permission to weaken the project's presets.

## 3. Serialization practice

Continue with [serialization contracts](serialization.md#3-serialization-practice).
Python representation, JSON wire shape, field exposure and schema completeness are
separate obligations. A model annotation does not imply a mapping output.

## 4. Typing with p and r

Continue with [typed outcomes](serialization.md#4-typing-with-p-and-r). The existing
error boundary preserves the original failure; consumer normalization and readmission
do not repair a producer contract.
