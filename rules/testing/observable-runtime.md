---
description: Test observable runtime behavior
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-08-30","route:both"]'
---

# Test observable runtime behavior

Measure the real public runtime or installed artifact before creating or
adapting a test. Tests validate current behavior; they never define it. Use only
public package roots, shared conftest owners, and typed fixtures. Do not mock,
monkeypatch, patch construction, import private modules, assert private methods,
copy configuration, freeze implementation shape, or hardcode owner values.

For `internal_flext`, all construction comes from `flext-tests` and its public
`tm`, `c`, `t`, `p`, `m`, and `u` facets. A local fixture binds scenario data
but never redeclares that machinery. Unit tests open no network socket and write
only inside fixture-owned storage; real integration services use their public
harness.

Every incremental, full, and CI pytest execution uses a selector-free root Make
verb (mutation by default; `APPLY=N` is the explicit dry-run override),
pytest-testmon, and the same external persistent database. The
full verb first completes the incremental verb, then runs
`--testmon --testmon-noselect` with that database. Raw pytest, direct test-file
selection, and cache deletion are prohibited.

A warning, skip, xfail, empty output, missing tool, missing report, zero
collection, unexecuted selected suite, caught exception, retry, or normalized
failure is RED. Only zero execution from a typed incremental testmon cache hit
is acceptable, and only when database integrity and complete deselection
accounting are proved; report it as a cache hit, never as tests passed. The
first exception, cause, and raw traceback escape unchanged.

See [`runtime-is-reality.md`](../workflow/runtime-is-reality.md) for the
runtime-first owner.
