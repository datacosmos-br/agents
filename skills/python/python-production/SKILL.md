---
name: python-production
description: "Production Python patterns and anti-patterns. USE FOR: writing or reviewing production Python code; structuring modules; exception design; type-annotated APIs. DO NOT USE FOR: debugging (python-debugging); parallelization (python-parallelization); quick throwaway scripts; notebooks."
license: MIT
metadata:
  bundle: python
  scope: universal
---

# Python Production Patterns

Full examples: [references/patterns.md](references/patterns.md).

## Structure

- `@dataclass` (frozen when immutable) for config — never loose dicts. Optional fields: `Optional[T] = None`.
- `pathlib.Path` always; `.resolve()`/`.exists()`/`.mkdir(parents=True, exist_ok=True)`.
- One logger per module (`getLogger(__name__)`); configure at entry points only; lazy formatting.
- Context managers for every resource.
- No mutable default arguments → sentinel `None`.
- `__all__` controls exports; minimal `__init__.py`; `__main__` guard in executables.

## Idiomatic toolkit

Prefer built-ins over manual loops: `Counter`, `defaultdict`, `itertools.chain/product/groupby`, generators for lazy pipelines, `functools.lru_cache` over hand memoization. Iterate, don't index (`zip`, `enumerate`, unpacking).

## Robustness

- `subprocess.run(["cmd", arg], check=True, capture_output=True, text=True)` — never `shell=True` with user input.
- Project base exception (`AppError`) + specific children; never bare `except:`; silence only expected cases (e.g., `KeyError` on cache miss).
- Enums for fixed sets; composition over inheritance; functions over stateless classes.
- Type annotations required on public API; `from __future__ import annotations` for forward refs.
- f-strings for interpolation; no `%` in new code; no wildcard imports.

## Critical rules

- Lazy imports only when profiling justifies them.
- Examples and anti-pattern pairs: [references/patterns.md](references/patterns.md).
