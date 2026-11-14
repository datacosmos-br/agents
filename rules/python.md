---
globs: ["*.py", "**/*.py", "pyproject.toml"]
description: Python facts its linters do not enforce
metadata:
  aihub.tags: '["decision:ADR-0038","effective:2026-11-03","route:both"]'
---

# Python

In internal projects, Rope owns Python semantics, refactorings and import edits, and an
authored ast-grep rule with its fix rewrites only a simple syntactic pattern; no other
tool rewrites Python semantics. A fork follows its upstream's tools; in every other
project, internal ones included, Ruff owns formatting and lint and Pyrefly owns
whole-program type analysis, both called from the command line by the project's own gate
verb under that project's own configuration, and no second formatter, linter or type
checker runs beside them. Each project's declared environment and lock owners apply. One
typed configuration owner per
project parses files, environment and arguments once and hands consumers frozen typed
values. Pydantic input is parsed once at the boundary with `model_validate` or
`model_validate_json` and travels inward as the model. Models compose by inheritance and
composition, each field declared once at its owner (skill `data-modeling`). Packages,
modules and directories are named by responsibility in PEP 8 form, never by number,
fragment or library. Bytecode caching stays on, and importing a module has no side
effects; everything else is the [law](law.md).
