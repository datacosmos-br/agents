---
description: A PR gate stays inside its offline time budget.
metadata:
  aihub.tags: '["decision:ADR-0031","effective:2026-10-01","route:both"]'
---

# Gate budget and offline generation

A PR gate completes within the budget declared once in the governance config key
`gates.pr_budget_minutes`, without relying on cache. The key is validated whenever the
bundle loads and is read through the published package as
`GovernanceBundle.load().config.gates.pr_budget_minutes`; no rule, skill, command, or
doc restates the number. Generation (`gen`) and verification (`check`, `test`) run
entirely offline; neither resolves a package, fetches a version manifest, or reaches a
network endpoint mid-run. The one exception is the pre-test provisioning of a host test
service, which fetches only digest-pinned inputs and only when the service's declared
fingerprint changes.

- Nothing slow runs in CI or at pre-commit, in absolute terms (tracker memory
  `operator-ruling-2026-10-01-precommit-fast-only`). CI and pre-commit run only fast
  external gates — lint, format, and gates of that kind — and CI adds only the test
  verb that `rules/workflow/canonical-commands.md` assigns to CI. Whole-program type
  checkers, code-smell audits, the project's own custom validators, and slow tests run
  only locally and at pre-push, where they block. Whether a gate is a fast external
  gate is typed metadata declared once in each project's gate registry; the CI workflow
  and the pre-commit hook derive their gate sets from it and never list gates
  themselves. That registry field is each project's implementation contract, not a
  field of this governance repository. Pre-commit is enabled and propagated by the
  project's generator and installed by its setup verb, never hand-installed per
  checkout.
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
