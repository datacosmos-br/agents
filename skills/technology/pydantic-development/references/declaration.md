## 1. model_rebuild is a defect — declarations are always strict

`Model.model_rebuild()` (and `_types_namespace` hacks) exist to patch
annotations that failed to resolve. In a strict fleet, every namespace that
declarations depend on — `config`, `settings`, `c`, `t`, `p`, `m`, `u`,
`base.py`, `services/`, `api.py`, `cli.py` — must be importable and resolved
at class creation. A required rebuild is therefore evidence of a broken
declaration: a forward reference to a name not exported by its facade, an
import cycle, a TYPE_CHECKING-only symbol used at runtime, or a model defined
in a function scope.

```python
class Node(m.FrozenModel):
    child: Node | None = None  # ok — module-level, resolves itself


Node.model_rebuild()  # violation — fix the declaration owner
```

Fix the owner (export the symbol through the correct facade, break the cycle
by moving the alias to `t`, hoist the model out of the function), never call
`model_rebuild`. The only tolerated form is inside the framework owner that
provably cannot know its types before runtime, documented at that owner.

## 2. Facade law (FLEXT members)

- flext-core is the sole owner of `pydantic`, `pydantic_settings`, and
  `pydantic_core` imports. Consumers import only through `m`, `t`, `p`, `u`,
  `r`, `e`:

```python
from flext_core import m, t, p, r  # ok
import pydantic  # violation outside flext-core
```

- A missing facade symbol is a gap to close at flext-core in the same change,
  never a reason for a direct import or a local re-export.
- Import discipline by tree — `src/`, `scripts/`, `examples/`, and `tests/`
  obey the same law with the same rigor: public facades only, no private
  module imports (`_utilities`, `_models`, `_parts` are non-public), no
  blanket lint excludes for any tree. Tests additionally consume `tm`/`tv`/`tt`
  fixtures and the unified `conftest.py`; scripts and examples are thin,
  typed consumers of the public surface, never second APIs.

## 3. Model MRO declaration — obligatory

Every model class extends an `m.*` preset. Declaring a consumer model on the
raw base is a violation; presets are the single source of configuration
(SSOT/DRY).

```python
class OrderLine(m.FrozenModel):  # ok — preset encodes config
    sku: t.NonEmptyStr
    qty: t.PositiveInt


class OrderLine(m.BaseModel):  # violation — raw base at consumer
    model_config = m.ConfigDict(frozen=True, strict=True)  # duplicates presets
```

- Facade families are namespace containers composed by explicit inheritance
  (`FlextModelsBase` chains its parts; `FlextModels` composes the families).
  Never create tuple-unpacked bases, merge classes, or parallel namespaces.
- One top-level class per module, ≤200 logical lines; declaration layers stay
  pure — models carry data (fields, validators, computed fields), behavior
  lives in `u`/services.
- Within flext-core, new shared presets join the existing
  `FlextModelsBase(_part02)` inheritance chain; consumers never redefine them.
- Models are the starting point of every boundary design: define the payload
  model first, then derive its `t` aliases, `p` ports, and service signatures
  from it — never the reverse, and never a dict shape standing in for the
  model.

## 4. Preset selection — read-only, mutable, strict

Choose by contract, not taste:

| Preset | Config essence | Use for |
| --- | --- | --- |
| `m.FrozenModel` | frozen + strict chain | read-only domain payloads, value data |
| `m.FrozenValueModel` / `m.Value` | frozen + value `__eq__`/`__hash__` | value objects compared by content |
| `m.ContractModel` | frozen, `validate_return`, `hide_input_in_errors` | immutable public contracts |
| `m.StrictModel` / `m.StrictBoundaryModel` | strict, `validate_default` | external ingress boundaries |
| `m.ManagedModel` | mutable, `validate_assignment`, `extra=forbid` | validated mutable state |
| `m.FlexibleInternalModel` | normalized, `extra=ignore` | internal domain plumbing |
| `m.TaggedModel` | `extra=forbid` + `tag` | discriminated-union variants |
| `m.Metadata` | frozen audit fields | metadata blocks (timestamps, tags, attributes) |
| `m.Entity` / `m.AggregateRoot` | id + timestamps + version + events | DDD entities/aggregates |
| `m.TimestampedModel` | created/updated timestamps | any time-audited record |

Decision order: read-only domain data → frozen; external input → strict;
mutable state → managed; never "flexible" at a boundary; never frozen where
the domain requires assignment.

## 5. Identity models — id, timestamps, version

Use `m.Entity` (composed `m.TimestampedModel` + `m.IdentifiableMixin` +
`m.VersionableMixin`):

- `unique_id`: `uuid4` default, non-empty string.
- `created_at`: frozen, UTC-enforced validator, ISO 8601 JSON serializer.
- `updated_at`: set in `model_post_init` when absent; must be ≥ `created_at`.
- `version`: optimistic-lock counter with minimum validation.
- `domain_events`: `MutableSequence` event-sourcing buffer (`p.HasDomainEvents`).
- Equality/hash is identity-based for `Entity`, value-based for `Value`.

```python
class Shipment(m.Entity):
    origin: t.NonEmptyStr


s = Shipment(origin="GRU")  # unique_id, created_at, version set
```

Compose mixins only through the documented order (timestamped first, then
identifiable, then versionable); timestamps are timezone-aware UTC, never
naive datetimes. Audit actor fields (`created_by`/`modified_by`) come from
`m.Metadata`, not ad-hoc fields.

## 6. Inheritance and MRO rules

- Explicit inheritance only; every base named. Mixin order matters: later
  bases win `ConfigDict` merges, so specific mixins come after general
  presets, matching the `Entity` composition.
- `model_post_init` overrides use `@override` and call `super()`.
- `__eq__`/`__hash__` must stay consistent: identity pair on entities, value
  pair on value objects; never mix.
- After model validators are instance methods (v2.12+ deprecated the
  `@classmethod` form):

```python
@u.model_validator(mode="after")
def check(self) -> Self:
    if self.end < self.start:
        raise ValueError("end before start")
    return self
```

- A validator defined on a base runs for subclasses; overriding replaces it.

## 7. Protocol declaration in p — obligatory

Cross-boundary dependencies are structural contracts in the `p` family, never
concrete model/service types (DIP):

- Nested inside the `FlextProtocols*` container; `@runtime_checkable class
  X(Protocol)`, extending `p.Base` when it generalizes an existing contract.
- Members are the minimal consumed capability (ISP): instance attributes and
  methods with `...` bodies and docstrings. Class-level Pydantic APIs stay on
  dedicated class protocols (`p.Model` instance API vs `ModelType`).
- Imports of `m`/`t` inside protocols are `TYPE_CHECKING`-only.
- Outcomes use `p.Result[T]`; routable messages use `CommandRoutable` /
  `EventRoutable` / `QueryRoutable`.

```python
class ShipmentSink(p.Base, Protocol):
    def accept(self, shipment: Shipment) -> p.Result[t.JsonPayload]: ...
```

A service annotating a dependency with a concrete model class or framework
type where a `p` protocol exists is a violation. New ports join the existing
protocol family; do not create parallel protocol namespaces.
