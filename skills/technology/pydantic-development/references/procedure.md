# Pydantic development procedure

## Pydantic development procedure

### 1. Composition and authority

Apply `$py-dev` first; it composes `$solid`. This procedure owns the Pydantic delta.
External behavior reference: official Pydantic documentation for the selected version.
`rules/python/pydantic.md` owns the boundary law; selected project ADRs own scoped
policy. This procedure explains their application rather than declaring another owner.
Generated files remain outputs; runtime behavior and project-owned configuration are
authoritative.

The references include research against
[Pydantic v2.14.1](https://github.com/pydantic/pydantic/tree/v2.14.1/docs).
That tag is not a universal dependency floor. The project declaration, selected lock
and loaded distribution establish its available behavior. Pydantic Settings has its
own version; never infer it from Pydantic's.

### 2. Version authority

- The project's declared dependency (pyproject dependency owner / config SSOT) is the
  only version truth. Never assume a global version, never upgrade or cap a floor inside
  a leaf change.
- Choose features at the declared floor and verify the installed version against
  the selected lock. A version observed in one workspace is not a universal
  dependency declaration; v3-only behavior is unavailable to a v2 project.
- A source citation carries the upstream tag used for that research (`@v2.14.1`
  for Pydantic and `@v2.15.0` for Pydantic Settings); re-verify it when the selected
  floor moves instead of turning the cited tag into a new project pin.
- A floor change is a workspace-level atomic migration: dependency SSOT, then templates,
  generated config, analyzers, tests, CI, docs.

### Native behavior checklist before implementation

Use the official [complete documentation](https://pydantic.dev/docs/validation/latest/llms-full.txt)
as a research index, not a version guarantee. Resolve every selected API against
the declared floor, selected lock and loaded runtime before changing its owner.

- Declare a complete closed string domain with its existing `StrEnum` type;
  reserve `Literal` for proper subsets and discriminator tags. This is the
  operator's domain declaration policy, not an upstream ban on `Literal`.
- Strict Python producers supply enum members and typed nested models. Raw JSON
  enters the JSON validator once; never serialize Python input merely to obtain
  JSON-mode coercion, relax a field, or retry failed validation.
- Resolve enum storage and protocol read/write types from the selected
  branch-matched FLEXT ADR-005/ADR-028 revision. A copied enum-value setting
  must not outlive its operator contract. Prove Python construction, defaults,
  assignment and JSON independently; enum storage does not itself make validation
  strict. Pass validated models by reference, without serialization and readmission.
- Compose existing presets and nested models; specialize generics explicitly.
  Keep constraints in reusable typed annotations and validators at their owner.
- Reuse the existing adapter and schema hooks before inventing custom validation.
  `InstanceOf` checks instances, not method signatures; protocol ports retain
  separate static and runtime consumer evidence.
- Distinguish DI from payload projection: FLEXT `t.Port` excludes its runtime
  dependency from JSON Schema; a serializable projected payload delegates its
  original concrete annotation through `GetPydanticSchema`. Preserve its native
  validation, serializers and schema once. Unresolved generic ports fail instead
  of selecting an unconstrained schema.
- Preserve the first exception through railway callbacks. A result conversion
  belongs only at the declared error boundary, never a recovery/default branch.

Upstream behavior references: [standard types](https://docs.pydantic.dev/latest/api/standard_library_types/),
[validators](https://docs.pydantic.dev/latest/concepts/validators/),
[custom types](https://docs.pydantic.dev/latest/concepts/types/), and
[adapter reuse](https://docs.pydantic.dev/latest/concepts/performance/).

### 3. settings, config, and the c·t·p·m·u wiring

Settings and config own distinct input authorities (ADR-005); a configurable fact has
one owner rather than a mirrored field in both. Each facade letter has one concern:

| Facade     | Receives                  | Owner of                                                                                       |
| ---------- | ------------------------- | ---------------------------------------------------------------------------------------------- |
| `c`        | constants                 | immutable invariants and closed vocabularies; reviewed configurable defaults remain in config |
| `t`        | typing                    | type aliases and annotated reusable types — the only alias owner                               |
| `p`        | protocols                 | structural contracts (`Protocol` classes) and `p.Result[T]`                                    |
| `m`        | Pydantic models           | model presets, payloads, entities, CQRS messages                                               |
| `u`        | helpers                   | pure utilities and behavior (validators helpers, dump, conversions)                            |
| `settings` | runtime-adjustable values | environment/CLI-overridable runtime inputs, typed `settings.<Namespace>.*` (pydantic-settings) |
| `config`   | static rules              | validated declarative rules from `config/*.yaml`, exposed as `config.<Namespace>.*`            |

Select values at a composition boundary. A domain service receives
the selected values and capabilities explicitly, not the global singletons.
Inherited supplier fields retain their actual public identity; do not manufacture a
namespace mirror merely to fit an example. New project domains use their declaring
namespace and the selected supplier's public contract.

- `settings` models read the environment; leaf modules never touch `os.environ` or
  process state directly — the knob enters through `settings`.
- Runtime-adjustable describes the source and supported update contract, not an
  unchecked mutable payload. Initial values, replacements and clones follow the
  settings owner's validation and source precedence. Do not impose a new freeze
  policy, mutate environment state from a leaf, or duplicate settings flags in config.
- `config` values are validated derivations of `config/*.yaml`; never re-declare,
  re-derive, or copy them into leaf modules, `c`, or models.
- Reviewed configuration owns static policy; settings owns runtime inputs. Both are
  validated states injected at the composition boundary, not a choice between
  untyped mappings and models. A configurable default keeps that same owner.
- Model-less configuration consumption, raw mappings as contracts, and local copies of
  config/settings values are violations. Payloads cross boundaries as `m` models
  validated on input and dumped on output.
- Models that need a configurable default receive it as an explicit field value at the
  composition root (`api`) — never by importing config deep in a declaration layer.

### Domain composition and MRO

Resolve family composition from the selected FLEXT ADR-014/ADR-028 and service
composition from ADR-019. Same-letter upstream facade inheritance publishes
capabilities; a real model extends its preset/data contract; nested model fields
represent containment; a service receives collaborators through ports. These
relationships are not interchangeable.

Python C3 method lookup, Pydantic field/configuration synthesis and DI are separate
mechanisms. Inspect effective configuration and fresh-import schema completeness;
do not infer them from a class header or repair disagreement with a copied preset.
An abstract runtime port is not a serializable payload schema. Preserve the
originating model's validation and serializers when ADR-018 projects a payload.

Model declarations may use native validators, serializers, computed fields and
lifecycle hooks for data invariants; business operations and external effects belong
to `u`/services. Register decorators through `m`, reusable annotation metadata through
`t`, and shared behavior through its `u` owner. Passing a validated instance avoids
duplicate parsing but does not prove subsequent mutable state remains valid; apply
the [boundary trust contract](boundary.md#2-validation-practice--centralized-owners).

For agent alignment, identify the selected owners and revisions before applying
examples, distinguish accepted targets from implemented behavior, and hand off
the actual public consumer, loaded origin, command, exit and limitations. A later
project decision updates its owner and consumers; it does not create another
universal rule body in each project's AGENTS.

### Static/runtime typing diagnosis

Read [the complete diagnosis procedure](typing-diagnosis.md) before attributing
constructor, field, overload or MRO findings to a checker. It retains the required
runtime/static evidence matrix and links to originating specifications.

### Project-owned model and service protocol projection

Read [project-owned protocol projection](typing-diagnosis.md#project-owned-model-and-service-protocol-projection)
and the selected ADR-018 before changing generation or consumers. That reference
retains full inventory, originating schema, semantic-owner and rollout requirements.

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

- [declaration.md](declaration.md) — facade law, presets and complete-declaration
  diagnosis, with stable continuation links for the composition topics.
- [composition.md](composition.md) — identity, inheritance, protocols, runtime ports,
  enum domains and minimal models under their selected project contracts.
- [boundary.md](boundary.md) — conversions, library exchange, changed trust state,
  native validation and continuation links for serialization/outcomes.
- [serialization.md](serialization.md) — output mode, schema/exposure, aliases,
  projected payloads and typed outcomes.
- [catalog.md](catalog.md) — capability inventory, performance, experimental policy,
  evidence and gates.
- [removals.md](removals.md) — detailed forms, replacements and source references;
  actual automatic cures require their own native rule/fixture evidence.
- [presets.md](presets.md) — contract-to-preset selection.
- [typing-diagnosis.md](typing-diagnosis.md) — runtime/static matrix, complete
  declarations and the project-owned protocol projection contract.
- [internals.md](internals.md) and [runtime.md](runtime.md) — versioned implementation
  research, with current policy kept at the declaring owners above.
