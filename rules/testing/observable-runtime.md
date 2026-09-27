---
description: Test observable runtime behavior
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-08-30","route:both"]'
---

# Test observable runtime behavior

Measure the real public runtime or installed artifact before creating or adapting a
test. Tests validate current behavior; they never define it. Use only public package
roots, shared conftest owners, and typed fixtures. Do not mock, monkeypatch, patch
construction, import private modules, assert private methods, copy configuration, freeze
implementation shape, or hardcode owner values.

For `internal_flext`, all construction comes from `flext-tests` and its public `tm`,
`c`, `t`, `p`, `m`, and `u` facets. A local fixture binds scenario data but never
redeclares that machinery. Unit tests open no network socket and write only inside
fixture-owned storage; real integration services use their public harness.

Every incremental, full, and CI pytest execution uses a selector-free root Make verb
invoked directly without an apply selector, pytest-testmon, and the same external
persistent database. The full verb first completes the incremental verb, then runs
`--testmon --testmon-noselect` with that database. Raw pytest, direct test-file
selection, and cache deletion are prohibited.

A warning, skip, xfail, empty output, missing tool, missing report, zero collection,
unexecuted selected suite, caught exception, retry, or normalized failure is RED. Only
zero execution from a typed incremental testmon cache hit is acceptable, and only when
database integrity and complete deselection accounting are proved; report it as a cache
hit, never as tests passed. The first exception, cause, and raw traceback escape
unchanged.

See [`runtime-is-reality.md`](../workflow/runtime-is-reality.md) for the runtime-first
owner.

## Fixture composition and the fail loop (operator ruling, 2026-09-12)

<!-- Why: registers 2026-09-12 operator rulings on test contracts (R21/R22/R25); extends this owner rather than duplicating it -->

Fixtures compose the gen-generated lazy-import pattern: one nested class per module,
built from `settings`/`config`/`c`/`t`/`p`/`m`/`u` and the shared conftest as the tests'
single source of truth (`u.Tests.*` builders), never a second ad hoc construction path.

A red test is fixed at its contract — conftest, the `c`/`t`/`p`/`m`/`u` facades, or the
fixture itself — never by loosening an assertion, skipping, or marking it xfail.
Classify every red test first: one that is fake, mocked, exercises implementation shape,
or bypasses the public interface is deleted — the test and any test-only production
symbol it required — and a real failure is fixed at its root-cause owner and rewired to
every consumer. Lowering a coverage floor to complete this extermination is acceptable;
every surviving test stays a real functional test.
