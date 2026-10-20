---
description: Test observable runtime behavior
metadata:
  aihub.tags: '["decision:ADR-0031","effective:2026-10-01","route:both"]'
---

# Test observable runtime behavior

Measure the real public runtime or installed artifact before creating or adapting a
test. Tests validate current behavior; they never define it. Use only public package
roots, shared conftest owners, and typed fixtures. Do not mock, monkeypatch, patch
construction, import private modules, assert private methods, copy configuration, freeze
implementation shape, or hardcode project-owned values — values that a configuration,
settings, or constants owner declares; inputs a fixture synthesizes are scenario data.
A test changes the process environment only through a scoped context that restores it
on exit (FLEXT: `u.Tests.env_vars_context`); a change that outlives the test fails it.

For `internal_flext`, all construction comes from `flext-tests` and its public `tm`,
`c`, `t`, `p`, `m`, and `u` facets. A local fixture binds scenario data but never
redeclares that machinery. Assertions use a `tm` matcher; a bare `assert` is allowed
only where no `tm` matcher expresses the check. Unit tests open no network socket and
write only inside fixture-owned storage; real integration services use their public
harness.

Every pytest execution goes through the test verbs declared only in
`rules/workflow/canonical-commands.md` (section "Test verbs"), which owns how they are
invoked, where each runs, and their testmon contract.

A warning, unexplained skip, xfail, empty output, missing tool, missing report, zero collection,
unexecuted selected suite, caught exception, retry, or normalized failure is RED. The
one acceptable zero execution is the typed `make test` cache hit of AGENTS.md law 14;
report it as a cache hit, never as tests passed. A capability deselection (below) is
neither a skip nor zero collection. The first exception, cause, and raw traceback escape
unchanged.

See [`runtime-is-reality.md`](../workflow/runtime-is-reality.md) for the runtime-first
owner.

## Host services and capability gating (operator decisions, 2026-09-29)

<!-- Why: registers the ADR-0031 test-program decisions on this owner rather than a new rule -->

A real integration service that a suite needs, such as a directory-server container, is
host state: one long-lived instance per host, shared by every checkout. Its declared
harness provisions it before the test clock starts (`gate-budget.md` (rule file)),
reuses it while healthy, and recreates it only when it is broken or its declared
fingerprint (image, configuration, schema, harness revision) changes, always under a
host lock. Tests share no data through it: each test works in its own namespace,
derived from the worker and run identity and removed at teardown, and the harness
sweeps stale namespaces. The service is not a borrowed environment; every checkout
uses the physical environment owned by its declared runtime root
(`rules/coordination/shared-venv-guard.md`).

A test declares the capability it actually consumes. The selected project's
applicability owner checks prerequisites before service-dependent fixtures. Retain
node identity, prerequisite and disposition for unavailable capabilities; never count
them as passed or infer applicability from a directory name alone. An executed test
whose available service fails is RED.

For FLEXT connectivity tests, the operator's 2026-10-10 prerequisite contract replaces
the older capability-deselection form: require a configured local untracked `.env` and
a reachable test environment. When either prerequisite is absent, the shared
`flext-tests` applicability owner skips the connectivity test before its
service-dependent fixture runs. Docker-dependent connectivity tests also skip in CI.
Pure unit and integration tests remain active; an `integration` marker alone never
makes a test a connectivity test.

These availability skips report unmet prerequisites, never successful connectivity
or production validation. Once the environment is available, authentication, protocol,
application and assertion failures remain failures. No other skip, fixture catch,
fallback or coverage exclusion is authorized by this prerequisite contract.

## Fixture composition and the fail loop (operator ruling, 2026-09-12)

<!-- Why: registers 2026-09-12 operator rulings on test contracts (R21/R22/R25); extends this owner rather than duplicating it -->

Fixtures compose the gen-generated lazy-import pattern: one nested class per module,
built from `settings`/`config`/`c`/`t`/`p`/`m`/`u` and the shared conftest as the tests'
single source of truth (`u.Tests.*` builders), never a second ad hoc construction path.

A red test is fixed at its contract — conftest, the `c`/`t`/`p`/`m`/`u` facades, or the
fixture itself — never by loosening an assertion, skipping, or marking it xfail.
Classify every red test first. Replace a fake, mocked, implementation-shaped or
private-interface test with public behavioral coverage preserving its failure
scenarios. Remove a test-only production symbol only after proving it has no remaining
consumer. Fix a real failure at its root-cause owner and rewire every consumer. Do not
lower coverage or weaken assertions to obtain a passing result.
