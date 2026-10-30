## 1. model_rebuild is a defect — declarations are always strict

Read [complete-declaration diagnosis](typing-diagnosis.md#complete-declarations-at-import)
for the cause analysis and owner repair. A schema required at import is not
qualified by a later rebuild; preserve the selected project's strict boundary.

## 2. Facade law (FLEXT members)

- flext-core is the sole owner of `pydantic`, `pydantic_settings`, and `pydantic_core`
  imports. Consumers import only through `m`, `t`, `p`, `u`, `r`, `e`:

Ordinary consumers use their declaring project's public facades; a model declaration
uses its selected upstream preset owner. Preserve the canonical family dependency
order instead of copying a deep import or manufacturing a local re-export.

- A missing facade symbol is a gap to close at flext-core in the same change, never a
  reason for a direct import or a local re-export.
- Import discipline by tree — `src/`, `scripts/`, `examples/`, and `tests/` obey the
  same law with the same rigor: public facades only, no private module imports
  (`_utilities`, `_models`, `_parts` are non-public), no blanket lint excludes for any
  tree. Tests additionally consume `tm`/`tv`/`tt` fixtures and the unified
  `conftest.py`; scripts and examples are thin, typed consumers of the public surface,
  never second APIs.

## 3. Model MRO declaration — obligatory

Every model class extends an `m.*` preset. Declaring a consumer model on the raw base is
a violation; presets are the single source of configuration (SSOT/DRY).

Choose the existing preset for the actual contract, as the
[selection table](presets.md) explains. A consumer declaration on the raw base with
a copied `ConfigDict` does not become conforming merely because its sample fields
validate.

- Facade families are namespace containers composed by explicit inheritance
  (`FlextModelsBase` chains its parts; `FlextModels` composes the families). Never
  create tuple-unpacked bases, merge classes, or parallel namespaces.
- One top-level class per module, within the flext-infra `loc-cap` ceiling; declaration
  layers stay pure —
  models carry data (fields, validators, computed fields), behavior lives in
  `u`/services.
- New shared presets belong to flext-core's existing public model family. Verify
  its composition at the selected supplier revision; consumers never redefine them
  or choose an owner from a historical private-part name.
- Models are the starting point of every boundary design: define the payload model
  first, then derive its `t` aliases, `p` ports, and service signatures from it — never
  the reverse, and never a dict shape standing in for the model.

## 4. Preset selection — read-only, mutable, strict

Read [preset selection](presets.md) for the required contract-to-preset mapping.
Its table describes intent; prove effective configuration on the selected public
model rather than treating a copied preset name as runtime evidence.

### FLEXT enum and schema contracts

Resolve enum storage and Python/JSON representation from the selected
branch-matched ADR-005/ADR-028 revision, including its explicit supersession.
Do not copy a volatile enum setting into this skill or a consumer preset.
Declare full string domains with their owning `c.*` `StrEnum`, retaining
subset and discriminator `Literal`s. Validate defaults, factories, assignment,
Python dumps, JSON and schema independently; strictness and enum storage are
different options. Generated reads/writes preserve the originating model's
actual contract, and frozen fields have no setter. Preset owners configure
once; consumers neither reconstruct validated values nor copy `ConfigDict`.

Import-time schema completeness is separate from lazy module imports. Where
ADR-028 requires complete declarations after import, `defer_build=True` is an
implementation gap, not permission to defer proof to later validation.

Native `use_enum_values=False` retains enum members in validated Python data;
`True` extracts primitive values during validation. JSON serialization is a
separate operation. The selected FLEXT ADR currently requires type preservation;
the older primitive-storage target is superseded. Keep enum defaults validated
and make generated read/write annotations match the concrete model's semantics.
See [the versioned configuration contract](https://github.com/pydantic/pydantic/blob/v2.14.1/pydantic/config.py).

## 5. Identity models — id, timestamps, version

Continue with [identity contracts](composition.md#5-identity-models--id-timestamps-version).
The selected public owner establishes fields, timestamp/version behavior and native
equality; an old field inventory does not establish the current API.

## 6. Inheritance and MRO rules

Continue with [data inheritance and MRO](composition.md#6-inheritance-and-mro-rules).
Facade composition, data inheritance, nested containment and service DI retain
different owners. Verify effective policy rather than treating C3 as config merging.

## 7. Protocol declaration in p — obligatory

Continue with [structural contracts](composition.md#7-protocol-declaration-in-p--obligatory)
and [protocol-typed fields](composition.md#8-protocol-typed-fields). The project-owned
payload projection preserves the original schema; a runtime DI port is a distinct
schema-excluded capability.
