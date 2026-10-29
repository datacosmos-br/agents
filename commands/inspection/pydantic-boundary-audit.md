---
name: pydantic-boundary-audit
description:
  Inventory Pydantic boundary violations in one repository against the flext removal
  catalog.
argument-hint: "<repository or workspace root>"
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-09-08","route:project"]'
---

# Pydantic boundary audit

Treat `$ARGUMENTS` as the repository (or workspace root with per-package scopes) to
audit. Read-only: this command never edits files.

1. Read `$pydantic-development` (removal catalog) and the repository's law before
   searching; the project's declared Pydantic floor is the version authority.
   For reported typing discrepancies, also apply its Static/runtime typing
   diagnosis section: retain actual engine/configuration/import identity and
   paired valid/invalid public-consumer evidence. Record missing runtime or
   editor evidence explicitly; a source inspection is not an executed probe.
2. Use the project's authenticated native inventory to search every owned Python
   module, including `src/`, `scripts/`, `examples/`, and `tests/`; these are examples,
   not a closed discovery list. Search for every catalog violation:
   bare `pydantic`/`pydantic_settings`/`pydantic_core` imports outside their owner;
   consumer models on a raw base or with a hand-written `ConfigDict` duplicating a
   preset; `model_rebuild()` calls; `model_construct()`;
   `SkipValidation`/`PlainValidator` without an owner justification;
   `serialize_as_any=True` call flags; catches of `ValidationError` that normalize or
   default; `json.loads` paired with `model_validate` and stdlib `json` at model
   boundaries; local per-call `TypeAdapter(...)`; `@validator` (v1) and `pydantic.v1`;
   `@classmethod` after model validators; `TypedDict`/`dict` used as public contracts;
   `os.environ` access or copied config/settings values in leaf modules.
3. Where the accepted branch-matched ADR-018 owns model/service protocol projection,
   apply its "Model and service protocol projection" contract and the skill's
   projection procedure. Report complete declaration and consumer accounting,
   runtime-sensitive uses, native reuse and measured profiling evidence; do not
   infer coverage from a sampled pilot or revive a historical branch's design.
   Also distinguish exhaustive enum-member `Literal` mirrors from legitimate
   subsets/discriminators; Python producer type defects from genuine JSON ingress;
   and inherited configuration assumptions from observed effective configuration.
   Resolve enum storage and protocol read/write types from the selected ADR-005/028;
   its type-preserving target supersedes the former primitive-storage instruction.
   Inspect defaults and Python/JSON behavior independently. Distinguish payload
   schema delegation from DI port instance checks,
   and report unconstrained schemas for unresolved generic ports. Compare actual
   import-time completeness with the declared contract, separately from lazy imports.
   Inventory strictness relaxation, validation retries, JSON round-trips used for
   coercion, duplicate port narrowing and exception recovery inside callbacks.
   Resolve native presets, nested/generic models, adapters and schema hooks before
   proposing a custom replacement. Cite the selected upstream feature's version
   support; the latest complete documentation is not the dependency declaration.
   Inspect shallow freezing, in-place mutation and instance revalidation separately;
   do not infer continuing validity from an earlier parse. Preserve local model classes
   and closures while diagnosing native namespace resolution. Report duplicated
   config/settings flags and source reads outside the composition owner, without
   inventing another settings freeze or source-precedence policy.
4. For each finding report: file:line, violation class, proposed owner-correct
   replacement, and whether `make mod` (ast-grep/Rope) can rewire it mechanically or a
   semantic owner fix is required.
5. Classify the result: counts per violation class, mechanical vs semantic split, and
   the ordered migration queue. Missing detection for a class is a finding too — name
   the enforcement gap (rule or detector) to add.

Return the inventory, the migration queue, and any owner-justified exceptions found
(each must cite its justification). A zero-violation result states the searched scope
explicitly; silence is never evidence.
