---
description: Declared verbs call native tools; locks, heavy runs, deadlines, test verbs
metadata:
  aihub.tags: '["decision:ADR-0038","effective:2026-11-03","route:both"]'
---

# Canonical commands

Every operation runs through declared verbs, each a thin call to its native tool that
does only its own operation ([law](../law.md)); a change is validated by its owner's
scoped command, and gates cover source, tests, examples and scripts alike. Configuration
declares the newest versions and only the upgrade verb locks them; every other verb
installs from the committed locks, offline. Heavy jobs pass host admission at idle
priority and run in the background or through authorized subagents
(`operator-order-2026-11-21-long-runs-in-background`). Native hooks own local commit
and push checks, and the [branch and PR rule](../git/gitflow-branch-pr.md) owns the
integration CI gate. Manual check, mod, fix, fmt and test runs are diagnostic work
outside the commit and push admission path
(`operator-decision-2026-11-21-hooks-and-ci-own-gates`). A pull-request gate fits
`gates.pr_budget_minutes` (`config/governance.json`). Every command runs under a
deadline, the 120-second bound of `operator-order-2026-10-24-make-always-with-timeout`
unless its project declares tighter, and a timeout is a failure fixed at its cause. Test
verbs: the incremental one runs Testmon on its persistent database, replaced only by its
schema migration; the full one runs without it and alone states a suite's time. An empty
run is an integrity-checked cache hit. Automated tests must run with private writable
state and without access to live user configuration, credentials, runtime sockets or
service control. The test entry point fails before running the suite if its isolation
boundary cannot be established. Runtime acceptance uses a separately provisioned
candidate and publishes only evidence. Hook, sandbox and MCP publication applies
only to the agent cohort explicitly authorized by the operator. Hook acceptance
also proves that the selected executable can launch on the recipient platform.
The complete native test suite must finish within
240 seconds of wall time, subject to any stricter declared deadline. An individual test
taking more than 2 seconds, including setup and teardown, requires causal profiling and
verified optimization. Every test has a hard 20-second limit
(`operator-order-2026-11-15-ci-test-budget`). A generated file names its writer and
regeneration command; a tool-written block changes only through that tool and loses to
any rule it contradicts. Text published to a forge or tracker comes from a file. Shell
invocations run one plain governed command per call, typed without an `rtk` prefix (rtk's
own hook rewrites eligible commands and never rewrites `git`), with no `;` chaining, pipes,
`&`, `/dev/null` or file redirections, `cd`, or `||` fallback, and never bypass a hook.
Work a declared verb owns (`python`, `ruff`, `pyrefly`, `uv`, `pip`, `pipx`, `mise`,
`pytest`) runs through the project's `make` or CLI verb. Extend that owner when a
capability is missing. `make setup` owns host publication and `make upg` owns version
changes (`operator-decision-2026-11-21-setup-publishes-upg-bumps-monopoly`). Setup
trusts, syncs and allows a new worktree itself. A consumer runs long work with observable
progress and uses the project's worktree sweep verb for cleanup.
