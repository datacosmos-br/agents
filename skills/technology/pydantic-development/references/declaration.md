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

How pydantic resolves an annotation while it builds a model:
- The globals are the module namespace of the class
  (`pydantic/_internal/_namespace_utils.py:255@v2.14.1`).
- The locals are, from lowest to highest priority (`_namespace_utils.py:259-285@v2.14.1`):
  - the parent namespace;
  - while a nested type is being resolved, the outermost type being built
    (`_namespace_utils.py:262-264@v2.14.1`);
  - `__type_params__`;
  - `vars(cls)`;
  - `{cls.__name__: cls}`.
- The parent namespace is a snapshot of the defining frame's locals, taken once at
  class creation (`pydantic/_internal/_model_construction.py:209-215@v2.14.1`,
  `pydantic/_internal/_typing_extra.py:134-195@v2.14.1`).

Inside a facade namespace class that snapshot is the outer class body still executing,
so the outer class name itself is not yet bound.

Consequences, each a defect in FLEXT:

- **`Outer.Sibling` in a nested model's annotation leaves the model incomplete at
  import.** The name fails to resolve, so pydantic marks the class incomplete
  (`_model_construction.py:202@v2.14.1`) and installs mock validators and serializers
  (`_model_construction.py:249@v2.14.1`, `_mock_val_ser.py:156@v2.14.1`). On first use
  they call `model_rebuild(raise_errors=False)` (`_mock_val_ser.py:170-172@v2.14.1`).
  FLEXT requires models complete at import (flext-sh/flext ADR-028 Decision 14); the
  flext-infra fresh-import gate reports any `__pydantic_complete__` false, and
  `ban-enclosing-family-field-reference` detects the form.
- **A bare sibling name is not the fix.** Pydantic resolves it from the snapshot, but a
  class block's names are not visible in nested blocks (Python Language Reference
  §4.2.2), and the FLEXT gates' checkers reject it. That is gate policy, measured in the
  FLEXT tree with evidence on FLEXT bead `flext-itpd1.11.7`.
- **Canonical form: a model referenced by a sibling lives in its own family module**,
  reached through that module's bound family class, so it is complete at import and
  every checker resolves it. `make mod` performs the extraction (flext-itpd1.11.7).

Other cases:

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
