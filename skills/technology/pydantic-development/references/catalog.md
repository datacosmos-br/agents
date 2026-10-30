# Pydantic catalog — capabilities, performance, experimental policy

Citations are versioned research references, not the project's dependency floor:
`@v2.14.1` denotes `pydantic/pydantic` and `@v2.15.0` denotes
`pydantic/pydantic-settings`. Re-verify availability, facade exposure and semantics
against the selected project before use.

## 1. Type ownership and capability inventory

- Domain aliases are PEP 695 `type`/`Annotated` declarations in `t`; reuse existing
  contracts such as `t.JsonPayload`. Native containers retain item types, mutability
  and fixed/variadic tuple arity; a generic synonym is not a domain contract.
- For FLEXT, the 2026-10-28 generic collection-wrapper retirement is owned by
  [ADR-028 Decision 7](https://github.com/flext-sh/flext/blob/0.12.0-dev/docs/architecture/adr/028-facade-boundary-orchestrators-declarative-enforcement.md#decision-7)
  and memory `operator-ruling-2026-10-28-generic-typing-wrapper-cutover`.
  Close consumers, rules, templates and docs, preserving validation metadata.
  Genuine domain generics and external constructs such as PEP 747 `TypeForm` remain.
- Reuse the public typed surface (`NonEmptyStr`, numeric constraints, `JsonValue`,
  `JsonMapping`) before adding aliases. No `Any`, `object`, bare containers or
  unparameterized generic fields. A declaration may remain generic, but admission
  needs its concrete/bound/constrained/default contract. Never replace an unresolved
  port with `Any` or duplicate its generic/schema registry.

The inventory routes each capability to its detailed owner; source mechanics are
versioned in [internals](internals.md) and [runtime](runtime.md).

| Capability family | Use and detailed reference |
| --- | --- |
| `ConfigDict`, `Field`, factories | [Presets](presets.md), field-specific defaults/aliases/constraints in [boundary](boundary.md) |
| `Annotated`, `StringConstraints`, before/after/wrap metadata | Reusable `t` constraints and [validation](boundary.md#2-validation-practice--centralized-owners) |
| `field_validator`, `model_validator`, `computed_field` | Native invariants and derived output; [composition](composition.md), no I/O |
| Plain/wrap and field/model serializers, polymorphic output | Owned shape and subclass exposure in [serialization](serialization.md) |
| Discriminators, `Tag`, `StrEnum`, narrow `Literal` | Actual variant/domain contracts in [composition](composition.md#9-closed-domains-are-strenum-members-of-c) |
| `InstanceOf`, DI `t.Port`, payload schema hooks | Distinct static/runtime/schema obligations in [composition](composition.md#8-protocol-typed-fields) |
| `RootModel`, parameterized models | Root or generic payloads; preserve specialization and [output shape](serialization.md) |
| `TypeAdapter`, direct JSON validation, `from_attributes` | `t` annotations, existing `u` runtime adapter and native [ingress](boundary.md#1-conversions--dict-typeddict-dataclass-json) |
| Validation/serialization context | Boundary facts in [validation](boundary.md), output facts in [serialization](serialization.md); no globals |
| `SecretStr`, `SecretBytes` | Sensitive representations; versioned source `pydantic/types.py:1819-1858@v2.14.1` |
| `FailFast`, `validate_call` | Explicit trade-offs at the declared [boundary](boundary.md#2-validation-practice--centralized-owners) |
| Settings sources | Native source precedence and merge in [runtime](runtime.md#8-pydantic-settings-source-pipeline) |
| `MISSING` and experimental APIs | Explicit absence and the admission policy below, not silent defaults |

## 2. Performance within the existing contract

- Validate JSON through native entry points (`model_validate_json`,
  `TypeAdapter.validate_json`), preserving configured validators and JSON semantics.
- Reuse adapters through their existing native owner; do not add a second cache.
- Use concrete containers when the existing domain promises them. An optimization
  does not authorize replacing a read-only `Mapping`, fixed tuple or mutable sequence
  with a different contract. Preserve genuine union semantics; tagged variants may
  use native discriminators, not guessed tags added to accelerate validation.
- Discriminated unions (`Field(discriminator=...)`) narrow at runtime through the
  literal `kind` check; after it, attribute access is type-safe. A defensive `getattr`
  fallback after narrowing hides drift from the union contract and is a violation.
- Where the selected project requires complete declarations at import, a
  `defer_build=True` preset is a producer defect. Lazy module loading does not
  waive schema completeness once that module loads. Elsewhere, upstream support
  for deferred building is a capability, not automatic project authorization.
- The official "use `TypedDict` over nested models" performance advice is rejected:
  `TypedDict` is not a FLEXT contract. Use narrower models, adapter reuse and the
  lifecycle-appropriate [preset](declaration.md#4-preset-selection--read-only-mutable-strict).
- Preserve the selected preset's string-cache and mutability settings. An upstream
  optimization does not authorize a consumer override or automatic feature enablement.

Profile the real consumer before tuning validators, adapters or nested payloads;
compare cold and unchanged execution with the same semantics and inputs. Native
capabilities are chosen for the current contract, not enabled as a feature checklist.
Reference: [v2.14.1 performance guidance](https://github.com/pydantic/pydantic/blob/v2.14.1/docs/concepts/performance.md).

## 3. Experimental features policy

`MISSING` sentinel, partial validation (`experimental_allow_partial`), pipeline API
(`validate_as`) and PEP 728 TypedDict extras are capabilities to evaluate, not
automatically admitted project behavior. A selected project decision must establish
the owner, version support, complete consumer contract and upgrade proof before use.
Partial or omitted invalid data never counts as full successful admission. Experimental
imports remain with the sole SDK import owner; a documentation example grants no bypass.
The absence of a runtime warning is not stability or upgrade evidence; retain the
versioned source and the selected owner's explicit decision for experimental use.

## 4. Advanced types catalog (verify the selected floor)

`StringConstraints`, `SerializeAsAny`, `FailFast`, `Discriminator`,
`InstanceOf`, `ValidateAs`, `RootModel`, `JsonValue`, `ImportString`,
`SecretStr`/`SecretBytes`,
`AliasChoices`/`AliasPath`, `computed_field`, `TypeAdapter`, `AliasGenerator`. Consumers
reach them through `m`/`t`; a missing symbol is closed at flext-core first.
This is a discovery index, not a mandate to use every API. Check the selected floor,
facade identity and consumer contract before adopting one; experimental status and
strict Python/JSON behavior are verified separately.

## 5. Removal catalog — what must not survive in code

The [removal reference](removals.md) keeps the detailed form, replacement and
versioned evidence in one table. The required boundary law remains
`rules/python/pydantic.md`; this discovery index grants no new exception or automatic
rewrite authority.

## 6. Evidence and gates

Run diagnostics, generation, repair, formatting, checks, and tests only through the root
Make dispatcher, invoking each verb directly without an apply selector. Before tests,
exercise the real runtime path (import the facade, validate a representative payload).
The boundary audit command (`$pydantic-boundary-audit`) inventories this removal catalog's
violations per repository and feeds `make mod` migrations. A claimed automatic cure
must identify its actual native rule and fixtures; the table alone does not establish
implemented coverage or semantic equivalence.
