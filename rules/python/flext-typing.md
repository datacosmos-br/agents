---
globs: "**/*.py"
description: FLEXT typing is strict; Any and object are grave violations
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-09-04","route:both"]'
---

# FLEXT typing: strict always — `Any` and `object` are grave violations

This rule applies only when the active project profile is `internal_flext`. A
third-party fork is excluded even when it contains Python files or depends on
FLEXT-compatible packages.

Using `Any` or bare `object` in a Python annotation is a grave violation, in any module,
test, or scratch script that lands in a governed tree. Typing is strict everywhere,
without exception and without temporary authorization.

Annotate by `t.*` type aliases and `p.*` protocols; for composites use one `t.*` alias
with `| None` at the outermost position.

- Import `p` and `m` under TYPE_CHECKING to avoid runtime cycles.
- Python 3.13 + Pydantic 2 only (`X | None`, builtin generics, `field_validator`,
  `model_validate`/`model_dump`); zero Pydantic v1.
- No `# type: ignore` / `noqa` shims — fix the type at its root.
- A type that seems to need `Any` or `object` is a missing alias or protocol: define
  that alias or protocol at its owner, then annotate strictly.
