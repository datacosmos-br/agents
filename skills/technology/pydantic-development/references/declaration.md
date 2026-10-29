## 1. model_rebuild is a defect — declarations are always strict

Read [complete-declaration diagnosis](typing-diagnosis.md#complete-declarations-at-import)
for the cause analysis and owner repair. A schema required at import is not
qualified by a later rebuild; preserve the selected project's strict boundary.

## 2. Facade law (FLEXT members)

- flext-core is the sole owner of `pydantic`, `pydantic_settings`, and `pydantic_core`
  imports. Consumers import only through `m`, `t`, `p`, `u`, `r`, `e`:

```python
from flext_core import m, t, p, r  # ok
import pydantic  # violation outside flext-core
```

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

```python
class OrderLine(m.FrozenModel):  # ok — preset encodes config
    sku: t.NonEmptyStr
    qty: t.PositiveInt


class OrderLine(m.BaseModel):  # violation — raw base at consumer
    model_config = m.ConfigDict(frozen=True, strict=True)  # duplicates presets
```

- Facade families are namespace containers composed by explicit inheritance
  (`FlextModelsBase` chains its parts; `FlextModels` composes the families). Never
  create tuple-unpacked bases, merge classes, or parallel namespaces.
- One top-level class per module, within the flext-infra `loc-cap` ceiling; declaration
  layers stay pure —
  models carry data (fields, validators, computed fields), behavior lives in
  `u`/services.
- Within flext-core, new shared presets join the existing `FlextModelsBase(_part02)`
  inheritance chain; consumers never redefine them.
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

Use the selected public entity preset and its declared fields, timestamp and
version contracts. Resolve its mixin order and equality/hash behavior from the
branch-matched model owner; a copied field inventory cannot establish that API.
Under FLEXT ADR-028 Decision 14, entity identity is compared explicitly by id,
while native Pydantic value equality remains intact. Mutable entities are
unhashable; a frozen model's hash still depends on hashable field values.

```python
class Shipment(m.Entity):
    origin: t.NonEmptyStr


s = Shipment(origin="GRU")  # unique_id, created_at, version set
```

Compose only the owner's documented mixins. Timestamp and audit fields reuse
their native declarations rather than a second consumer implementation.

## 6. Inheritance and MRO rules

- Explicit inheritance only; every base named. Inspect effective `model_config`
  through the public model before composing presets. Pydantic documents that
  multiple-base configuration merging does not currently follow Python MRO;
  never infer C3 configuration semantics or repair a conflict with a local copy.
  See [configuration inheritance](https://docs.pydantic.dev/latest/concepts/config/).
- `model_post_init` overrides use `@override` and call `super()`.
- Preserve native model-value equality for entities and value objects. Compare entity
  identity explicitly by id; do not restore identity-based `__eq__`/`__hash__`.
  Frozen models are hashable only when their field values support hashing.
- After model validators are instance methods (v2.12+ deprecated the `@classmethod`
  form):

```python
@m.model_validator(mode="after")
def check(self) -> Self:
    if self.end < self.start:
        raise ValueError("end before start")
    return self
```

- A validator defined on a base runs for subclasses; overriding replaces it.
- Compose nested models by fields and model specialization by explicit generic
  arguments; neither is namespace-facade inheritance. An enclosing family's name
  is not bound while its body executes, so qualify annotations through an already
  bound declaring owner. Do not copy configuration from an outer model into a
  nested one: each native model owns its configuration boundary.
- `frozen=True` prevents attribute reassignment, not mutation inside a contained
  list or mapping. `validate_assignment=True` checks assignment, not in-place
  container changes. Choose immutable containers only where the domain requires
  them; freezing a model is not proof that all reachable data remains valid.

## 7. Protocol declaration in p — obligatory

Cross-boundary dependencies are structural contracts in the `p` family, never concrete
model/service types (DIP):

- Nested inside the `FlextProtocols*` container; `@runtime_checkable class X(Protocol)`,
  extending `p.Base` when it generalizes an existing contract.
- Members are the minimal consumed capability (ISP): instance attributes and methods
  with `...` bodies and docstrings. Class-level Pydantic APIs stay on dedicated class
  protocols (`p.Model` instance API vs `ModelType`).
- Imports of `m`/`t` inside protocols are `TYPE_CHECKING`-only.
- Outcomes use `p.Result[T]`; routable messages use `CommandRoutable` / `EventRoutable`
  / `QueryRoutable`.

```python
class ShipmentSink(p.Base, Protocol):
    def accept(self, shipment: Shipment) -> p.Result[t.JsonPayload]: ...
```

A service annotating a dependency with a concrete model class or framework type where a
`p` protocol exists is a violation. New ports join the existing protocol family; do not
create parallel protocol namespaces.

Under the project's ADR-018, a serializable payload projected to `p` preserves
its original concrete validation and serialization through `GetPydanticSchema`.
It does not become an ADR-019 DI port: `t.Port` is a FLEXT annotation based on
native hooks, excludes the dependency from JSON Schema and checks runtime member
presence rather than signatures or nested payloads. Resolve generic parameters
at their owner; never substitute an unconstrained schema for an unresolved port.
