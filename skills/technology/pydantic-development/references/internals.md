# Pydantic internals — why the practices make consumer code lighter

This is versioned research, not another project contract. Citations retain the
upstream tags used by the source author (`pydantic/pydantic` v2.14.1 and
`pydantic/pydantic-settings` v2.15.0). Resolve the project's actual Pydantic,
pydantic-core and settings distributions separately; the tags do not establish
their installed versions. Re-verify a mechanism before relying on it at a new floor.

## 1. Architecture: Python defines, Rust validates and serializes

- Model definition (fields, config, decorators, private attributes) lives in Python;
  the native core executes validation and serialization with declared callbacks.
  Their shared schema interface is the *core schema*, a typed dict with a `type` key,
  stored on the class as
  `__pydantic_core_schema__` (`docs/internals/architecture.md:4-48@v2.14.1`).
- Only the fixed core-schema set is supported; there are no custom schema types
  (`docs/internals/architecture.md:39-45@v2.14.1`).
- Serialization rules travel inside the same schema under `serialization`; JSON
  Schema is derived from the core schema (`docs/internals/architecture.md:81-131@v2.14.1`).

The native schema connects compiled core validation with Python callbacks. A Python
validator or serializer remains Python code invoked by that runtime; it is not
automatically compiled into Rust. Reuse the existing owning schema and callbacks
instead of duplicating admission in consumers, and profile actual callback costs.

## 2. Class creation pipeline and its cost

At class creation `ModelMetaclass.__new__` (`pydantic/_internal/_model_construction.py`):

1. Captures the defining frame's locals as a weak-valued snapshot
   (`:209-210`, `:780-797@v2.14.1`).
2. Collects fields from the reversed MRO with lenient annotation evaluation
   (`pydantic/_internal/_typing_extra.py:235-291@v2.14.1`).
3. Unless `defer_build`, calls `complete_model_class` (`:248-259@v2.14.1`), which
   generates the core schema through the single `GenerateSchema` entry point
   (`pydantic/_internal/_generate_schema.py:356@v2.14.1`), cleans it (Rust gather,
   inlining of single-use refs, `_generate_schema.py:2847-2911@v2.14.1`), then builds
   `__pydantic_validator__` and `__pydantic_serializer__`
   (`_model_construction.py:621-675@v2.14.1`).
4. Sets `__pydantic_complete__ = True` and calls the `__pydantic_on_complete__` hook
   (`_model_construction.py:677-680@v2.14.1`; `pydantic/main.py:956-965@v2.14.1`).

Reuse already built in:

- Within one build, repeated types collapse to `definition-ref` schemas
  (`_generate_schema.py:2776-2845@v2.14.1`).
- A nested complete model reuses its stored schema (`_generate_schema.py:839-856@v2.14.1`)
  and its prebuilt Rust validator/serializer (`pydantic-core/src/common/prebuilt.rs:7-43@v2.14.1`).
- PEP 695 `type` aliases become one named definition per build, keyed by alias
  identity (`_generate_schema.py:1390-1408@v2.14.1`).

These mechanisms are reuse points, not a universal performance guarantee. Preserve
the data contract and measure the real import, validation and serialization path
before claiming that a different composition is smaller or faster.

## 3. Forward references, mocks and why `model_rebuild` appears

- Field evaluation is lenient: an unresolved name marks the field incomplete
  (`pydantic/_internal/_fields.py:474-476,509-510@v2.14.1`).
- An incomplete class gets `MockCoreSchema`/`MockValSer` placeholders
  (`pydantic/_internal/_mock_val_ser.py:156-194@v2.14.1`). Any first use triggers an
  automatic `model_rebuild(_parent_namespace_depth=5)`; failure raises
  `class-not-fully-defined` (`_mock_val_ser.py:96-105@v2.14.1`).
- Resolution namespace: module globals of the class's module, then locals in
  priority order — parent-frame snapshot, the outermost type being built, PEP 695
  type params, the class `__dict__`, and `{ClassName: cls}` so self-references always
  resolve (`pydantic/_internal/_namespace_utils.py:238-287@v2.14.1`).
- The parent-local snapshot is taken at definition; later local bindings are not
  added to that snapshot (`docs/internals/resolving_annotations.md:136-140@v2.14.1`).
  Module globals and later validation have their own resolution lifetime; do not
  generalize the snapshot rule into a ban on every local or nested declaration.

An outer namespace still being built or an unavailable sibling can leave an
annotation unresolved. Diagnose the actual creation scope, exported identity and
import lifetime through [complete declarations](typing-diagnosis.md#complete-declarations-at-import).
A required schema must be complete at the project's declared boundary; upstream's
ability to build it on first use is different evidence. Repair a proven owner defect
without guessed namespace maps, a copied preset or an automatic runtime-class hoist.

## 4. Configuration merge is shallow and follows `bases` order

`ConfigWrapper.for_model` (`pydantic/_internal/_config.py:148-189@v2.14.1`):

- Copies each base's `model_config` in **`bases` order, not MRO**; a later base
  overrides an earlier one (`docs/concepts/config.md:181-183@v2.14.1`).
- Then applies the class body `model_config`, then class keyword arguments (highest).
- The merge is key-by-key `dict.update`: nested values such as `json_schema_extra`
  are replaced, never deep-merged.
- Config does not propagate into nested models; each model is its own boundary
  (`docs/concepts/config.md:207-261@v2.14.1`).

The selected preset owns its effective policy. Data inheritance, namespace facade
composition, contained models and dependency injection remain separate relationships;
inspect effective fields/configuration and public behavior rather than inferring them
from a class header. See [the native configuration warning](https://docs.pydantic.dev/latest/concepts/config/).

Continued in `runtime.md` (validation runtime, equality, TypeAdapter, settings sources).
