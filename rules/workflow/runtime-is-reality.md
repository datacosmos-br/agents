---
description: Verify runtime reality before tests or completion claims
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-08-28","route:both"]'
---

# Reality is the running system; tests are checks, not the SSOT

First reproduce and validate the declared public import, API, CLI, daemon,
service, generated consumer, deployed artifact, or other real runtime selected
by the project. Verify its revision or release identity. Only after that
contract is measured may tests be created, adapted, or invoked. An editable
checkout, test assertion, snapshot, local cache, generated copy, or stale
environment does not define runtime behavior.

A test that preserves removed behavior, copied configuration, private shape, or
a hardcoded owner value is defective and is rewritten or deleted. Use the
public root and typed shared fixtures. Missing public constants and invalid
dependency wiring are exercised through the actual import and call path.

Every test path uses its selector-free root Make verb with `APPLY=Y`, the same
external persistent testmon database, and the observable-test rule. The full
verb runs incremental selection first and no-selection second without clearing
the database. Warning, skip, empty output, missing tool/report, zero collection,
catch, retry, or normalization is RED. A typed incremental testmon cache hit may
execute zero tests only with database integrity and complete deselection
accounting; it is reported as a cache hit, never as tests passed.

The newest declared tool version owns its diagnostics. Do not cap, downgrade,
substitute, suppress, or relabel a result. Correct the owner and rerun the same
root Make verb; the first exception and raw traceback remain causal.
