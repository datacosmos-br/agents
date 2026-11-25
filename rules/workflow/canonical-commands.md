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
checks on the index only, so read `git status` before committing: unstaged edits are
absent from the commit the hooks passed. Required integration CI must pass on the
exact PR head before the reviewed merge. Every plan phase, and the plan's end, ends
with its PR merged into the integration branch before the next phase starts; a
missing integration PR is a grave failure
(`operator-order-2026-11-21-integration-pr-every-phase`). The ordered cycle and its
verbs are owned by the [delivery doctrine](agent-delivery-doctrine.md#the-delivery-cycle);
outside it an agent hand-runs a gate only to diagnose a red result. Full mod and full
tests require an explicit order. Scope authorizes runtime publication and proof.
Repair red hooks, CI and integration findings at their owner, including warnings,
and follow [law 8–10](../law.md)
(`operator-decision-2026-11-21-hooks-and-ci-own-gates`).
Long work, queue waits and CI monitoring run in the background or through authorized
subagents while independent work advances. Heavy jobs pass host admission at idle
priority (`operator-order-2026-11-21-long-runs-in-background`); host load, admission
refusals, queue waits and API quota exhaustion never stop a slice: the agent continues it
and fixes the measured cause at its owner, coordinating with the other sessions, without
weakening FLEXT rules or changing what lint, CI and make verbs check
(`operator-decision-2026-11-22-aggregate-prs-own-load`). A long verb started
from an agent terminal runs detached in its worktree (`setsid nohup make <verb>`, output
in `<worktree>/nohup.out`) and is awaited by one background
`tail --pid=<pid> -n 0 -f <worktree>/nohup.out`, never a shell loop
(`operator-order-2026-11-22-long-verbs-detached`). A pull-request gate
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
own hook rewrites eligible commands and never rewrites `git`), with no `;` or `&&`
chaining, pipes, `&`, `/dev/null` or file redirections, `cd`, `env -C` or a tool's `-C`
(`git -C`, `go -C`, `make -C`; a lane command runs with its worktree as working directory
or through the project's lane verb, direnv and rtk automating;
`operator-order-2026-11-21-worktree-cwd-only`), or `||` fallback, and never bypass a hook.
A nested shell (`sh -c`, `bash -c`) is not a plain command; stage, commit and push are
separate calls. A hook or classifier denial is answered in the form its message and the
owning tool's docs give, never by a reworded retry or a raw fallback, and a refused verb
is repaired at its owner. Lane creation, commit, push, pull request, merge and retirement
go through the project's lane verbs, and a wait is one native watching command
(`gh pr checks --watch`, `gh run watch`), never a shell loop
(`operator-order-2026-11-21-no-forbidden-command-forms`).
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

A lane commits and pushes once its [delivery cycle](agent-delivery-doctrine.md#the-delivery-cycle) is green; the commit and push hooks run the declared fast gates without provisioning and never wait on the full-form queue, and the integration CI decides the merge. Only `make setup` publishes to the host and only `make upg` changes versions. Long-running work runs in the background or in a subagent, and its end wakes the session. Work that another lane holds is integrated, never waited on: merge its branch `--no-ff` or `git cherry-pick -x` its commits. Related slices may merge `--no-ff` into one lane, be validated together and land as one PR with one green integration CI, each Bead still recording its own evidence (`operator-decision-2026-11-22-aggregate-prs-own-load`). Done is merged at the integration tip and active at runtime with proof.
A red test, warning or finding on the integration tip is fixed in the same cycle by the actor that finds it; "pre-existing" and "another lane's" never defer it, and a commit is named by its full SHA read from Git, never guessed (`operator-order-2026-11-21-done-no-excuses`).
