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
priority; under load a run narrows, never waits or reports blocked. A long command or
job runs in the background or in a subagent, never blocking its session on a poll
(`operator-order-2026-11-21-long-runs-in-background`). Delivery is edit, `git add` of
explicit paths, `git commit -F <file>`, `git merge --no-ff` of the integration tip, push,
a pull request from `--body-file`, integration CI on its exact head, merge commit, then
deploy and runtime proof: the commit and push hooks run check, mod, fix, fmt and tests,
so an agent hand-runs a gate only to diagnose a red hook or CI, while the generation
verbs a change needs (gen, and upg on a pin change) still run
(`operator-decision-2026-11-21-hooks-and-ci-own-gates`). A pull-request gate fits
`gates.pr_budget_minutes` (`config/governance.json`). Every command runs under a
deadline, the 120-second bound of `operator-order-2026-10-24-make-always-with-timeout`
unless its project declares tighter, and a timeout is a failure fixed at its cause. Test
verbs: the incremental one runs Testmon on its persistent database, replaced only by its
schema migration; the full one runs without it and alone states a suite's time. An empty
run is an integrity-checked cache hit. The complete native test suite must finish within
240 seconds of wall time, subject to any stricter declared deadline. An individual test
taking more than 2 seconds, including setup and teardown, requires causal profiling and
verified optimization. Every test has a hard 20-second limit
(`operator-order-2026-11-15-ci-test-budget`). A generated file names its writer and
regeneration command; a tool-written block changes only through that tool and loses to
any rule it contradicts. Text published to a forge or tracker comes from a file. Shell
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
