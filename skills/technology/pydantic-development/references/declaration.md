## 1. model_rebuild is a defect — declarations are always strict

`Model.model_rebuild()` (and `_types_namespace` hacks) exist to patch annotations that
failed to resolve. In a strict fleet, every namespace that declarations depend on —
`config`, `settings`, `c`, `t`, `p`, `m`, `u`, `base.py`, `services/`, `api.py`,
`cli.py` — must be importable and resolved at class creation. A required rebuild is
therefore evidence of a broken declaration: a forward reference to a name not exported
by its facade, an import cycle, a TYPE_CHECKING-only symbol used at runtime, or a model
defined in a function scope.

```python
class Node(m.FrozenModel):
    child: Node | None = None  # ok — module-level, resolves itself


Node.model_rebuild()  # violation — fix the declaration owner
```

Fix the owner (export the symbol through the correct facade, break the cycle by moving
the alias to `t`, hoist the model out of the function), never call `model_rebuild`.
The operator ruling of 2026-10-24 bans it without exception; `ban-model-rebuild` is an
error-severity rule.

How pydantic resolves names (`internals.md` §3): module globals, then the defining
frame snapshot taken at class creation, then `{ClassName: cls}`. Names bound later are
never visible through the snapshot, and inside a facade namespace class the outer name
is not yet bound while its body executes. Patterns that always complete at class
creation:

- Declare nested models in dependency order; a model references only siblings defined
  above it **by bare name**, `t`/`c`/`p` aliases, or itself.

Measured on pydantic 2.14.1 (study script, 2026-10-24):

| Reference inside a namespace class | Complete at definition | First use |
| --- | --- | --- |
| earlier sibling, bare name | yes | ok |
| earlier or later sibling, `Outer.Name` path | no (mock) | ok — automatic rebuild from module globals |
| later sibling, bare name | no | `class-not-fully-defined` |
| subclass field referencing a parent-namespace model | yes | ok |

```python
class FlextFooModels(FlextModels):
    class Line(m.FrozenModel):
        sku: t.NonEmptyStr

    class Order(m.FrozenModel):
        lines: tuple[Line, ...]  # ok — complete at class creation
        replaces: Order | None = None  # ok — self-reference always resolves
        tail: Later | None = None  # violation — later sibling: reorder the declarations
```

The `Outer.Name` path resolves only lazily (the class stays a mock until first use and
pays the build then); prefer bare names in dependency order so every model is complete
when its module finishes importing.

- Mutual recursion between two models is a modeling smell; express it as one model with
  a self-reference or a discriminated union of variants declared in order.
- A cross-module cycle is an import-direction defect; move the shared type down to the
  lower facade instead of rebuilding.

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

Choose by contract, not taste:

| Preset                                    | Config essence                                    | Use for                                        |
| ----------------------------------------- | ------------------------------------------------- | ---------------------------------------------- |
| `m.FrozenModel`                           | frozen + strict chain                             | read-only domain payloads, value data          |
| `m.FrozenValueModel` / `m.Value`          | frozen + value `__eq__`/`__hash__`                | value objects compared by content              |
| `m.ContractModel`                         | frozen, `validate_return`, `hide_input_in_errors` | immutable public contracts                     |
| `m.StrictModel` / `m.StrictBoundaryModel` | strict, `validate_default`                        | external ingress boundaries                    |
| `m.ManagedModel`                          | mutable, `validate_assignment`, `extra=forbid`    | validated mutable state                        |
| `m.FlexibleInternalModel`                 | normalized, `extra=ignore`                        | internal domain plumbing                       |
| `m.TaggedModel`                           | `extra=forbid` + `tag`                            | discriminated-union variants                   |
| `m.Metadata`                              | frozen audit fields                               | metadata blocks (timestamps, tags, attributes) |
| `m.Entity` / `m.AggregateRoot`            | id + timestamps + version + events                | DDD entities/aggregates                        |
| `m.TimestampedModel`                      | created/updated timestamps                        | any time-audited record                        |

Decision order: read-only domain data → frozen; external input → strict; mutable state →
managed; never "flexible" at a boundary; never frozen where the domain requires
assignment.

Continued in `composition.md` (identity, inheritance, protocols, domains, compression).
