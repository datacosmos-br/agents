# Pydantic development procedure

## Pydantic development procedure

### 1. Composition and authority

Apply `$py-dev` first; it composes `$solid`. This procedure owns the Pydantic delta.
External behavior reference: the official Pydantic documentation for the project's
declared version. Project law: this file and the `rules/python/pydantic.md` rule.
Generated files remain outputs; runtime behavior and project-owned configuration are
authoritative.

### 2. Version authority

- The project's declared dependency (pyproject dependency owner / config SSOT) is the
  only version truth. Never assume a global version, never upgrade or cap a floor inside
  a leaf change.
- Choose features at the declared floor, read from the project's lock — never from this
  text. Every citation in these references carries the upstream tag it was verified
  against (`@v2.14.1` for pydantic + pydantic-core 2.50.1, `@v2.15.0` for
  pydantic-settings); re-verify them against the pinned upstream source when the floor
  moves. v3-only behavior is never available.
- A floor change is a workspace-level atomic migration: dependency SSOT, then templates,
  generated config, analyzers, tests, CI, docs.

### 3. settings, config, and the c·t·p·m·u wiring

Two independent typed objects own every configurable fact (ADR-005); each facade letter
has exactly one concern:

| Facade     | Receives                  | Owner of                                                                                       |
| ---------- | ------------------------- | ---------------------------------------------------------------------------------------------- |
| `c`        | constants                 | invariants and scalar defaults (private constant modules exposed through `c`)                  |
| `t`        | typing                    | type aliases and annotated reusable types — the only alias owner                               |
| `p`        | protocols                 | structural contracts (`Protocol` classes) and `p.Result[T]`                                    |
| `m`        | Pydantic models           | model presets, payloads, entities, CQRS messages                                               |
| `u`        | helpers                   | pure utilities and behavior (validators helpers, dump, conversions)                            |
| `settings` | runtime-adjustable values | environment/CLI-overridable runtime inputs, typed `settings.<Namespace>.*` (pydantic-settings) |
| `config`   | static rules              | validated declarative rules from `config/*.yaml`, exposed as `config.<Namespace>.*`            |

```python
from flext_core import config, settings  # consumption is single-form

workers = settings.Dispatcher.workers  # runtime-tunable knob
strict = config.Dispatcher.strict_mode  # validated static rule
```

- `settings` models read the environment; leaf modules never touch `os.environ` or
  process state directly — the knob enters through `settings`.
- `config` values are validated derivations of `config/*.yaml`; never re-declare,
  re-derive, or copy them into leaf modules, `c`, or models.
- Model-less configuration consumption, raw mappings as contracts, and local copies of
  config/settings values are violations. Payloads cross boundaries as `m` models
  validated on input and dumped on output.
- Models that need a configurable default receive it as an explicit field value at the
  composition root (`api`) — never by importing config deep in a declaration layer.

### 4. pydantic-settings

- `BaseSettings` defaults to `extra="forbid"`, `validate_default=True` and
  `arbitrary_types_allowed=True` (`pydantic_settings/main.py:617-656@v2.15.0`); FLEXT
  settings extend the flext-core settings preset, which owns those choices once.
- Source priority (highest first): CLI when enabled, init kwargs, environment, dotenv,
  secrets directory, field defaults (`docs/index.md:3096-3106@v2.15.0`). Sources are
  deep-merged, so a lower source fills nested keys a higher one omits
  (`pydantic_settings/main.py:485-507@v2.15.0`).
- Extra sources (YAML, TOML, JSON, pyproject) are added only through
  `settings_customise_sources` (`pydantic_settings/main.py:264-286@v2.15.0`); setting
  `yaml_file` without the source only warns (`main.py:587-615@v2.15.0`).
- Nested models come from the environment through `env_nested_delimiter`
  (`sources/providers/env.py:267-338@v2.15.0`); nested defaults update partially only
  with `nested_model_default_partial_update` (`docs/index.md:639-688@v2.15.0`).
- A custom file source implements `_read_file(path) -> dict[str, Any]`
  (`sources/base.py:237-239@v2.15.0`); that mapping is pydantic-settings' contract and
  the settings model validates it. Do not pre-validate it into a second model or keep a
  per-call `TypeAdapter` there.
- Runtime overrides are typed constructor arguments or the documented underscore
  kwargs (`_env_file`, `_case_sensitive`, …; `main.py:193-392@v2.15.0`), never manual
  `Mapping` merges in FLEXT code.

### Reference parts

- [declaration.md](declaration.md) — `model_rebuild` cure by extraction to a family
  module (FLEXT gate policy), facade law, obligatory model MRO, preset selection.
- [composition.md](composition.md) — identity models, inheritance and config merge,
  protocol declaration in `p`, protocol-typed fields, StrEnum domains, minimal models.
- [boundary.md](boundary.md) — conversions, library data exchange, updating validated
  data, centralized validation practice.
- [serialization.md](serialization.md) — serialization practice, aliases, typing with
  `p` and `r`.
- [catalog.md](catalog.md) — capability inventory, performance, experimental policy,
  evidence and gates.
- [removals.md](removals.md) — every banned form with its replacement and source.
- [internals.md](internals.md) — architecture, class creation, forward references,
  config merge.
- [runtime.md](runtime.md) — Rust validation runtime, equality, TypeAdapter cost,
  pydantic-settings source pipeline.
