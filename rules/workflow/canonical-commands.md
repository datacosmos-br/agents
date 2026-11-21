---
description: Declared verbs call native tools; locks, heavy runs, deadlines, test verbs
metadata:
  aihub.tags: '["decision:ADR-0038","effective:2026-11-03","route:both"]'
---

# Canonical commands

Every operation uses its declared native verb ([law](../law.md)). Gates cover source,
tests, examples and scripts. Configuration declares versions. Setup installs the
committed locks offline, and upg changes pins. Stage explicit paths, commit from a
message file, merge a moved integration tip with `git merge --no-ff`, push, and open
the PR from `--body-file`. Native commit and push hooks run each project's declared
checks. Required integration CI must pass on the exact PR head before the reviewed
merge. Every plan phase, and the plan's end, ends with its PR merged into the
integration branch before the next phase starts; a missing integration PR is a grave
failure (`operator-order-2026-11-21-integration-pr-every-phase`). An agent hand-runs check, mod, fix, fmt or tests only to diagnose a red result.
Run gen when generated surfaces change and upg when pins change. Full mod and full
tests require an explicit order. Scope authorizes runtime publication and proof.
Repair red hooks, CI and integration findings at their owner, including warnings,
and follow [law 8–10](../law.md)
(`operator-decision-2026-11-21-hooks-and-ci-own-gates`).
Long work, queue waits and CI monitoring run in the background or through authorized
subagents while independent work advances. Heavy jobs pass host admission at idle
priority (`operator-order-2026-11-21-long-runs-in-background`). A pull-request gate
fits `gates.pr_budget_minutes` (`config/governance.json`). Every command runs under
the 120-second deadline of `operator-order-2026-10-24-make-always-with-timeout`
unless its project declares tighter, and a timeout is a failure fixed at its cause. Test
verbs: the incremental one runs Testmon on its persistent database, replaced only by its
schema migration; the full one runs without it and alone states a suite's time. An empty
run is an integrity-checked cache hit. Automated tests use private writable state with
no access to live user configuration, credentials, runtime sockets or service control.
The test entry point fails if it cannot establish isolation. Runtime acceptance uses a
separate candidate and publishes evidence. Hook, sandbox and MCP publication applies
only to the authorized agent cohort. Hook acceptance proves the executable launches
on the recipient platform. The complete native test suite must finish within
240 seconds of wall time, subject to any stricter declared deadline. An individual test
taking more than 2 seconds, including setup and teardown, requires causal profiling and
verified optimization. Every test has a hard 20-second limit
(`operator-order-2026-11-15-ci-test-budget`). A generated file names its writer and
regeneration command; a tool-written block changes only through that tool and loses to
any rule it contradicts. Text for a tracker, forge or mail comes from a file (`--file`,
`--body-file`, or `xargs -0 -a <file>` when the CLI has no file flag). Shell
invocations run one plain governed command per call, typed without an `rtk` prefix (rtk's
own hook rewrites eligible commands and never rewrites `git`), with no `;` chaining, pipes,
`&`, `/dev/null` or file redirections, `cd`, `env -C` or a tool's `-C` (a lane runs with
its worktree as working directory, direnv and rtk automating;
`operator-order-2026-11-21-worktree-cwd-only`), or `||` fallback, and never bypass a hook.
A nested shell (`sh -c`, `bash -c`) is not a plain command, and a refused verb or a
denied action is repaired at its owner, never replaced by a raw fallback.
Work a declared verb owns (`python`, `ruff`, `pyrefly`, `uv`, `pip`, `pipx`, `mise`,
`pytest`) runs through that project's `make` or CLI verb; a missing capability extends
that owner. `make setup` is the only verb that publishes (the host tool registry
included) and `make upg` the only one that changes a version
(`operator-decision-2026-11-21-setup-publishes-upg-bumps-monopoly`); setup trusts,
syncs and `direnv allow`s a new worktree on its own, host load never refuses it, and
every verb or tool that rewrites an `.envrc` re-allows it
(`operator-order-2026-11-21-setup-self-sufficient`); never run
silent commands exceeding 10 seconds without progress, and use the project's worktree
sweep verb for worktree/branch cleanup.

## Delivery

A lane commits and pushes as soon as its change is complete: the pre-commit and pre-push hooks run the Make gates, and the integration CI decides the merge; no session runs check, fix, fmt or tests by hand only to commit. Only `make setup` publishes to the host and only `make upg` changes versions. Long-running work runs in the background or in a subagent, and its end wakes the session. Work that another lane holds is integrated, never waited on: merge its branch `--no-ff` or copy its fix byte for byte. Done is merged at the integration tip and active at runtime with proof.
