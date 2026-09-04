---
globs: **/*.py
---

# FLEXT typing: no Any, annotate by aliases and protocols

Never annotate with `Any`/`object` or with concrete classes. Annotate by `t.*`
type aliases and `p.*` protocols; for composites use one `t.*` alias with
`| None` at the outer level.

- Import `p` and `m` under `TYPE_CHECKING` to avoid runtime cycles.
- Python 3.13 + Pydantic 2 only (`X | None`, builtin generics, `field_validator`,
  `model_validate`/`model_dump`); zero Pydantic v1.
- No `# type: ignore` / `noqa` shims — fix at the root.
