# Pydantic development procedure

## Pydantic development procedure

### 1. Composition and authority

Apply `$py-dev` first; it composes `$solid`. This procedure owns the Pydantic delta.
External behavior reference: the official Pydantic documentation for the project's
declared version. Project law: this file and the `rules/python/pydantic.md` rule.
Generated files remain outputs; runtime behavior and project-owned configuration are
authoritative.

For the current FLEXT baseline, use the
[Pydantic v2.14.1 reference](https://github.com/pydantic/pydantic/tree/v2.14.1/docs)
for API semantics, the selected lock for resolution and the loaded distribution for
runtime proof. Pydantic Settings has its own version; never infer it from Pydantic's.

### 2. Version authority

- The project's declared dependency (pyproject dependency owner / config SSOT) is the
  only version truth. Never assume a global version, never upgrade or cap a floor inside
  a leaf change.
- Choose features at the declared floor and verify the installed version against
  the selected lock. A version observed in one workspace is not a universal
  dependency declaration; v3-only behavior is unavailable to a v2 project.
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

Two independent typed objects own every configurable fact (ADR-005); each facade letter
has exactly one concern:

| Facade     | Receives                  | Owner of                                                                                       |
| ---------- | ------------------------- | ---------------------------------------------------------------------------------------------- |
| `c`        | constants                 | immutable invariants and closed vocabularies; reviewed configurable defaults remain in config |
| `t`        | typing                    | type aliases and annotated reusable types — the only alias owner                               |
| `p`        | protocols                 | structural contracts (`Protocol` classes) and `p.Result[T]`                                    |
| `m`        | Pydantic models           | model presets, payloads, entities, CQRS messages                                               |
| `u`        | helpers                   | pure utilities and behavior (validators helpers, dump, conversions)                            |
| `settings` | runtime-adjustable values | environment/CLI-overridable runtime inputs, typed `settings.<Namespace>.*` (pydantic-settings) |
| `config`   | static rules              | validated declarative rules from `config/*.yaml`, exposed as `config.<Namespace>.*`            |

```python
from flext_cli import config, settings

name = config.Cli.name  # reviewed supplier identity
debug = settings.debug  # runtime input
```

The example selects values at a composition boundary. A domain service receives
the selected values and capabilities explicitly, not the global singletons.

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

### Reference parts

- [declaration.md](declaration.md) — obligatory model MRO, `model_rebuild`
  extermination, facade law, preset selection, identity models, inheritance, protocol
  declaration in `p`.
- [boundary.md](boundary.md) — conversions (dict, TypedDict, dataclass, JSON),
  centralized validation practice, serialization practice, typing with `p` and `r`.
- [catalog.md](catalog.md) — types and annotations, performance, experimental policy,
  advanced types, the removal catalog, evidence and gates.
- [presets.md](presets.md) — contract-to-preset selection.
- [typing-diagnosis.md](typing-diagnosis.md) — runtime/static evidence and originating
  specifications for constructor, facade, overload and MRO findings.

### Static/runtime typing diagnosis

Read [the complete diagnosis procedure](typing-diagnosis.md) before attributing
constructor, field, overload or MRO findings to a checker. It retains the required
runtime/static evidence matrix and links to originating specifications.

### Project-owned model and service protocol projection

Read [project-owned protocol projection](typing-diagnosis.md#project-owned-model-and-service-protocol-projection)
and the selected ADR-018 before changing generation or consumers. That reference
retains full inventory, originating schema, semantic-owner and rollout requirements.
