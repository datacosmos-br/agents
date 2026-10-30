# Pydantic development procedure

## Pydantic development procedure

### 1. Composition and authority

Apply `$py-dev` first; it composes `$solid`. `rules/python/pydantic.md` owns the
boundary law and selected project ADRs own scoped policy. This procedure routes
their application; generated files remain outputs, not another authority.

### 2. Version authority

- Distinguish the declared dependency floor, selected lock and loaded distribution.
  Do not upgrade/cap a dependency in a leaf or infer Settings' version from Pydantic.
- Research tags (`@v2.14.1` Pydantic, `@v2.15.0` Settings) are citations, not universal
  pins. Re-verify availability against official source at the selected floor; v3-only
  behavior is unavailable to a v2 project.
- A floor change is a workspace-level atomic migration: dependency SSOT, then templates,
  generated config, analyzers, tests, CI, docs.

### Native behavior checklist before implementation

Use the official [complete documentation](https://pydantic.dev/docs/validation/latest/llms-full.txt)
as a research index, then follow the detailed owner:

- [Declarations](declaration.md#flext-enum-and-schema-contracts): full enum domains,
  narrow literals, central storage policy, preserved strictness/defaults and separate
  Python/JSON/schema proofs.
- [Boundary](boundary.md): parse once, reuse admitted values, changed trust state and
  native source grammar; no JSON readmission, field relaxation or retry workaround.
- [Composition](composition.md): existing presets, explicit generics, runtime ports
  versus projected payloads; instance checks do not establish signatures or schemas.
- [Serialization](serialization.md#4-typing-with-p-and-r): first cause preserved through
  railway callbacks and conversion only at the declared error boundary.

### 3. settings, config, and the c·t·p·m·u wiring

Settings and config own distinct input authorities (ADR-005); a configurable fact has
one owner rather than a mirrored field in both. Each facade letter has one concern:

| Owner | Responsibility |
| --- | --- |
| `c` | Stable invariants/vocabularies; configurable defaults stay in config |
| `t` | Domain aliases and reusable annotation metadata |
| `p` | Structural capabilities, consumption contracts and outcomes |
| `m` | Presets, validated data, entities and messages |
| `u` | Reusable algorithms/adapters and approved runtime factories |
| `settings` | Typed environment/CLI runtime inputs |
| `config` | Reviewed validated policy and declarations |

Select values once at API/CLI/daemon composition and inject validated data and ports.
Leaves do not read process globals, copy singleton state or import config into model
declarations for defaults. Project domains use `config.<Namespace>.*` and
`settings.<Namespace>.*`; inherited supplier fields keep their actual public identity.

Runtime-adjustable does not mean unchecked or necessarily mutable. Initial values,
replacements and clones retain the settings owner's validation and precedence; do
not impose a freeze policy, mutate environment state in leaves or mirror settings in
config. Reviewed defaults retain their source and enter models as explicit values.

### Domain composition and MRO

Resolve facade composition from selected ADR-014/ADR-028, payload projection from
ADR-018 and DI from ADR-019. [Composition](composition.md) distinguishes facade
inheritance, model inheritance, containment and injected capabilities. C3 lookup
does not prove effective Pydantic configuration or complete fresh-import schemas;
never repair disagreement by copying presets. Runtime ports and payload schemas
remain separate contracts.

Native hooks own data invariants; external effects belong to `u`/services.
Decorators enter through `m`, reusable annotation metadata through `t`. Apply the
[trust contract](boundary.md#2-validation-practice--centralized-owners) when state
changes after admission.

For agent alignment, identify the selected owners and revisions before applying
examples, distinguish accepted targets from implemented behavior, and hand off
the actual public consumer, loaded origin, command, exit and limitations. A later
project decision updates its owner and consumers; it does not create another
universal rule body in each project's AGENTS.

### Static/runtime typing diagnosis

Use the [diagnosis matrix](typing-diagnosis.md) before attributing constructor,
field, overload or MRO findings to a checker; retain runtime and static evidence.

### Project-owned model and service protocol projection

Use [protocol projection](typing-diagnosis.md#project-owned-model-and-service-protocol-projection)
and selected ADR-018 for inventory, originating schema, semantic owner and rollout.

### 4. pydantic-settings

Extend the selected flext-core settings preset; it owns validation/default policy.
The [source pipeline](runtime.md#8-pydantic-settings-source-pipeline) retains native
precedence, deep merge, custom sources, nested input and runtime overrides with
versioned citations. Library-local source mappings are not a second FLEXT payload:
do not pre-validate them into another model or create a per-call adapter.

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
