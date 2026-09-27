---
description: "The runtime is the acceptance authority: when a test contradicts observed runtime behavior, the test's premise is rewritten in the same commit as the contract change — the runtime is never contorted to satisfy a stale test."
capsule_summary: |
  Operator ruling 2026-09-27 (session gascity-23): "tests are more broken than
  the runtime; what counts is validating and making the runtime work". Measured
  case: the dc-use reconciliation took the canonical tree's doctor files and
  its smaller test file, dropping the fork's drift-detection tests that the
  resource ledger pinned as Medium owners — the ledger dangled until the tests
  were restored from the pre-merge parent, not waved through.
metadata:
  aihub.tags: '["effective:2026-09-27", "route:both", "source:session-gascity-23"]'
---

# Runtime first, contract tests second

## The order of authority

1. **Observed runtime behavior through the public consumer contract** decides
   what is correct.
2. **Tests verify** that behavior; they do not define it. A test that pins a
   stale contract (a guard that moved layers, a fixture that predates a
   topology change, an expectation the runtime outgrew) is rewritten in the
   same commit that changes the contract — with the premise documented in its
   docstring.
3. A green suite with a broken runtime is a red result wearing paint: the
   runtime red wins every time.

## What this forbids

- Contorting the runtime so a stale test stays green (the test is the defect).
- Marking, skipping, or weakening the test to escape the rewrite (skips are
  red wearing green paint).
- "Pre-existing failure" as a terminal verdict: pre-existing reds are adopted
  and fixed forward at their owner, like any other red.

## What it requires

- The reconciliation commit carries BOTH the contract change and the test
  rewrite, with the premise of each documented.
- Runtime validation is performed by running the real thing (CLI from a
  neutral directory, real git, real remotes) and reading its typed output —
  before, not after, the PR.
- Canonical assertions only (`pytest.raises(m.ValidationError)`, not invented
  exception shims); the zero-baseline standard applies to the fixer too.
