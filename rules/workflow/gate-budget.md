---
description: A PR gate stays inside its offline time budget.
metadata:
  aihub.tags: '["decision:ADR-0031","effective:2026-09-29","route:both"]'
---

# Gate budget and offline generation

A PR gate completes in 10 minutes or less without relying on cache. Generation (`gen`)
and verification (`check`, `test`) run entirely offline; neither resolves a package,
fetches a version manifest, or reaches a network endpoint mid-run. The one exception is
the pre-test provisioning of a host test service, which fetches only digest-pinned
inputs and only when the service's declared fingerprint changes.

- Profiling (cProfile, a coverage instrumenter, or any other collector) is opt-in and
  off by default on every gate-path runner. A pytest runner with always-on profiling is
  a toolchain defect, not an acceptable baseline.
- Coverage collection is opt-in, invoked by its own explicit target. A gate that always
  measures coverage inflates every run's budget for a signal most runs do not need.
- The test runner's budget covers the budgeted test phase only. Host test-service
  provisioning runs before the test clock in the pre-test hook, bounded by its own
  deadline; tests declared `slow` run in their own phase, each within a per-item bound.
  Neither exclusion raises a limit, bypasses testmon selection, or makes a failure
  anything but RED.
- Independent gate steps run in parallel, not sequentially, when they share no mutable
  state. A sequential check suite that could run its independent probes concurrently is
  a budget defect at its owner.
- Network access observed during `setup`, `gen`, `check`, or `test` — a version-manifest
  fetch, an ad hoc registry install mid-run, an unpinned remote resolution — is a defect
  of the toolchain owner (flext-infra), never of the consumer invoking the gate. The
  consumer never works around it with a retry, a cache, or a skip; it escalates to the
  toolchain owner.

Observed: cProfile enabled unconditionally in a pytest runner, `tokei` installed from
crates.io during `make gen`, and a doctor command running its checks sequentially —
each pushed a gate past its budget or broke offline execution.

Compose with `rules/runtime/strict-execution.md` and
`rules/workflow/canonical-commands.md`.
