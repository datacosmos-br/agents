---
description: "One heavy gate at a time: pre-push matrices, full suites, and dependency resolution never run concurrently — shared temp/git state under load manufactures flakes that cost more to diagnose than the serialization saved."
capsule_summary: |
  Measured 2026-09-26/27 (session gascity-23): a pre-push matrix, a full test
  suite, and a dependency resolution running together produced an atomic-write
  timeout flake, a misattributed test red, and three blind push retries.
  Diagnosing any of them required re-running the very gates that were racing.
metadata:
  aihub.tags: '["decision:ADR-0021","effective:2026-09-27","route:both"]'
---

# Heavy gate serialization

## The rule

One heavy gate per machine at a time. A heavy gate is any of: a pre-push
matrix, a full test suite, a dependency resolution/lock, a release build, or
an acceptance job. Targeted single-test runs are cheap and may interleave;
gates may not.

## Why (measured, not hypothetical)

- Atomic file writes timed out under load and failed an unrelated test
  (`write_atomic_bytes` during fixture setup), costing a full diagnosis cycle
  that a rerun on a quiet machine made vanish.
- Test-shard reds under contention misattributed causes (host-load family)
  and forced re-runs to separate real defects from races.

## Diagnostics discipline

- Every gate run captures its shard logs persistently
  (`LOCAL_TEST_LOG_DIR=...` on gascity, or the repo's equivalent): diagnosing
  a refusal without shard logs costs a full extra gate cycle.
- A gate failure without a captured log is re-run with capture before any
  code is touched — the failure you guess at is not the failure you have.
- Treat slow as a signal: a step that takes multiples of its usual time is a
  defect to diagnose (contention, leak, wedge), not a queue to wait out.
