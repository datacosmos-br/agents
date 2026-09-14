# Pydantic development procedure

# Pydantic development procedure

## 1. Composition and authority

Apply `$py-dev` first; it composes `$solid`. This procedure owns the Pydantic
delta. External behavior reference: the official Pydantic documentation for
the project's declared version. Project law: this file and the
`rules/python/pydantic.md` rule. Generated files remain outputs; runtime
behavior and project-owned configuration are authoritative.

## 2. Version authority

- The project's declared dependency (pyproject dependency owner / config SSOT)
  is the only version truth. Never assume a global version, never upgrade or
  cap a floor inside a leaf change.
- Choose features at the declared floor. Workspace installs Pydantic
  2.14.0b1 (stable line 2.13.5); capabilities documented as "New in v2.13" are
  available, v3-only behavior is not.
- A floor change is a workspace-level atomic migration: dependency SSOT, then
  templates, generated config, analyzers, tests, CI, docs.

## 3. settings, config, and the c·t·p·m·u wiring

Two independent typed objects own every configurable fact (ADR-005); each
facade letter has exactly one concern:

| Facade | Receives | Owner of |
| --- | --- | --- |
| `c` | constants | invariants and scalar defaults (private constant modules exposed through `c`) |
| `t` | typing | type aliases and annotated reusable types — the only alias owner |
| `p` | protocols | structural contracts (`Protocol` classes) and `p.Result[T]` |
| `m` | Pydantic models | model presets, payloads, entities, CQRS messages |
| `u` | helpers | pure utilities and behavior (validators helpers, dump, conversions) |
| `settings` | runtime-adjustable values | environment/CLI-overridable runtime inputs, typed `settings.<Namespace>.*` (pydantic-settings) |
| `config` | static rules | validated declarative rules from `config/*.yaml`, exposed as `config.<Namespace>.*` |

```python
from flext_core import config, settings  # consumption is single-form

workers = settings.Dispatcher.workers  # runtime-tunable knob
strict = config.Dispatcher.strict_mode  # validated static rule
```

- `settings` models read the environment; leaf modules never touch `os.environ`
  or process state directly — the knob enters through `settings`.
- `config` values are validated derivations of `config/*.yaml`; never
  re-declare, re-derive, or copy them into leaf modules, `c`, or models.
- Model-less configuration consumption, raw mappings as contracts, and local
  copies of config/settings values are violations. Payloads cross boundaries
  as `m` models validated on input and dumped on output.
- Models that need a configurable default receive it as an explicit field
  value at the composition root (`api`) — never by importing config deep in a
  declaration layer.

## Reference parts

- [declaration.md](declaration.md) — obligatory model MRO, `model_rebuild`
  extermination, facade law, preset selection, identity models, inheritance,
  protocol declaration in `p`.
- [boundary.md](boundary.md) — conversions (dict, TypedDict, dataclass, JSON),
  centralized validation practice, serialization practice, typing with `p` and
  `r`.
- [catalog.md](catalog.md) — types and annotations, performance, experimental
  policy, advanced types, the removal catalog, evidence and gates.
