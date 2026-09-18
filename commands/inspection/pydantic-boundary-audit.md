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
2. Search `src/`, `scripts/`, `examples/`, and `tests/` for every catalog violation:
   bare `pydantic`/`pydantic_settings`/`pydantic_core` imports outside their owner;
   consumer models on a raw base or with a hand-written `ConfigDict` duplicating a
   preset; `model_rebuild()` calls; `model_construct()`;
   `SkipValidation`/`PlainValidator` without an owner justification;
   `serialize_as_any=True` call flags; catches of `ValidationError` that normalize or
   default; `json.loads` paired with `model_validate` and stdlib `json` at model
   boundaries; local per-call `TypeAdapter(...)`; `@validator` (v1) and `pydantic.v1`;
   `@classmethod` after model validators; `TypedDict`/`dict` used as public contracts;
   `os.environ` access or copied config/settings values in leaf modules.
3. For each finding report: file:line, violation class, proposed owner-correct
   replacement, and whether `make mod` (ast-grep/Rope) can rewire it mechanically or a
   semantic owner fix is required.
4. Classify the result: counts per violation class, mechanical vs semantic split, and
   the ordered migration queue. Missing detection for a class is a finding too — name
   the enforcement gap (rule or detector) to add.

Return the inventory, the migration queue, and any owner-justified exceptions found
(each must cite its justification). A zero-violation result states the searched scope
explicitly; silence is never evidence.
