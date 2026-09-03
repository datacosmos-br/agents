---
globs: ["*.py", "**/*.py", "pyproject.toml"]
description: Python rules
metadata:
  aihub.tags: '["decision:plan-00","effective:2026-09-02","route:both"]'
---

# Python rules

These rules apply to Python only. Use the project's declared Python versions,
frameworks, package manager, typing policy, and canonical command facade. Never
inject another repository's development or orchestration contract into a
generic Python project.

## Validation

1. Discover native commands from `make help` or the repository's declared
   equivalent.
2. Run the real Python entry point or public API before adapting tests.
3. Run every declared lint, format, type, test, build, security, and packaging
   gate affected by the change.
4. Zero errors, warnings, skips, missing tools, or ignored diagnostics.
5. Preserve command, cwd, exit code, decisive output, commit SHA, and scope in
   Git/PR/CI evidence.

Do not replace a missing canonical command with an ad hoc raw invocation. Fix
the owner or report the exact blocker.

## Language and typing

- Follow the Python versions declared by the project; do not assume a global
  version.
- Use `from __future__ import annotations` when supported and useful for the
  declared compatibility range.
- Prefer precise types, protocols at public boundaries, built-in generics where
  supported, and explicit `X | None` semantics.
- NEVER use `Any` or bare `object` in operator-owned Python. Strict typing is
  absolute: every parameter, return, and attribute is precisely typed, and the
  project's type gates run strict. A narrowly unavoidable third-party stub gap
  must follow project policy and retain its exact diagnostic code and
  rationale; it never licenses `Any` in first-party signatures.
- The prohibition covers tests too: test code is typed with the same strictness
  as production code — fixtures, params, and returns included.
- Parse untrusted input once into a typed model at the boundary. Use the
  project's declared validation/model owner; do not impose Pydantic on projects
  that do not use it.
- Public APIs document parameters, return values, errors, side effects, and
  compatibility.

## Module structure and namespaces

- Declared projects compose code through the canonical single-letter
  namespaces — `c` (constants), `t` (types), `p` (protocols), `m` (models),
  `u` (utilities) — plus typed `services`/`api` facades. Import and use them;
  never re-declare parallel constants, models, protocols, or helpers locally.
- Modules are organized as nested classes inside a typed owner class (the
  flext/ai-hub pattern: one owner class per file, nested classes as
  sub-owners), never loose top-level function soup.
- Services own behavior, models own data, protocols own boundaries, constants
  own values. A new capability lands in its owner layer; if the owner layer is
  missing, create it through the declared facade before writing logic.

## Revalidation after mutation

- After every code mutation, immediately revalidate with the project's
  declared gates: formatter/linter (`ruff`), type checker (`pyrefly`/mypy),
  and the duplication scanner (`jscpd`) alongside the test gate. A gate the
  project does not declare is not invented; one it declares is never skipped.

## Errors and resources

- CLI boundaries, validators, and orchestrators never catch workflow
  exceptions or translate them. The original traceback and causal chain escape.
- Catch only inside cleanup or rollback. Retain the original exception as the
  one re-raised and attach every secondary cleanup/rollback failure to its
  causal evidence.
- Never aggregate independent validation defects, swallow errors, invent
  success/default data, return ambiguous sentinels, or convert structured
  failures into untyped strings.
- Use context managers and structured concurrency for owned resources.
- Cancellation and timeouts must stop only resources owned by the invocation.
- Retry is prohibited. A failed operation terminates the invocation.

## Design and migration

- Search existing owners and consumers before adding code.
- Keep functions/modules cohesive and follow repository complexity/size gates;
  never invent a universal line-count threshold.
- Complete refactors in one cycle: build the final owner, migrate every
  in-scope consumer, delete superseded code/tests/docs, and prove no stale
  reference remains.
- Prefer immutable data where practical and explicit dependency injection at
  boundaries.
- Tests assert observable behavior, including material failure and
  should-not-trigger cases; they do not assert private construction.

## Portability

No private absolute path, symlink, editable dependency to another checkout,
cross-repository reference, inherited secret, or project state under `/tmp`.
Technology skills are installed only in explicitly selected projects where
local markers prove Python.
