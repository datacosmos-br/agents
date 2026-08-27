# Session protocol

## Start a repository session

1. Read [authority and scope](00-authority-and-scope.md),
   [shared contracts](01-shared-contracts.md), and the selected repository
   runbook.
2. Read the latest ledger events for the repository/work-id without printing
   secrets.
3. Confirm the repository remote, branch, worktree, dirty state, upstream,
   integration SHA, merge-base, and local commits.
4. Re-query GitHub PRs, reviews, checks, branch protection, and remote branches.
5. Run the repository's help/bootstrap inspection command before choosing a
   gate.
6. Compare the current state with the runbook snapshot. Current Git/GitHub
   evidence wins; update the ledger when it differs.
7. Confirm no command in the intended phase invokes the suspended runtime.
8. Append a `session-started` event with current SHAs, phase, and first exact
   command.

Do not create a second lane when the runbook names an existing clean lane.

## Work checkpoint

After each repository-state change, append one ledger event containing:

- work-id and repository;
- phase and state transition;
- changed files and intent;
- source SHA for absorbed WIP;
- validation command, exit, and decisive output;
- next exact command or blocking condition.

Re-run operator-correction reconciliation after three material state changes,
at phase boundaries, and before landing. New operator instructions replace
contradictory text in this package; do not leave both versions active.

## Handling concurrent work

- Fetch and inspect before assuming a branch or PR is unchanged.
- Never discard concurrent commits or dirty files.
- When integration advances, merge it into the work branch with `--no-ff` and
  revalidate.
- When another actor changes the same owner, compare intent and preserve both
  valid contracts. Stop if the contracts conflict.
- Record superseded evidence instead of rewriting ledger history.

## Blocking report

A blocking handoff must contain:

```text
repository/work-id
phase and commit SHA
exact command
exit code
decisive error
owner that must change
files already changed
tests already passed
next safe command
```

Do not propose a bypass, fallback, suppression, alternate model, alternate
server, or destructive cleanup.

## Landing handoff

Before merging, record:

- integration SHA merged into the lane;
- runtime and full-gate evidence;
- PR URL and unresolved thread count;
- required-check conclusions;
- expected merge method.

After merging, record:

- GitHub merge SHA and parents;
- proof the SHA is reachable from the integration branch;
- detached post-merge worktree path;
- post-merge runtime and gates;
- branch/worktree cleanup evidence;
- final state `LANDED_VERIFIED_PENDING_TRACKER`.

## End-of-session minimum

An unfinished session leaves the worktree intact and reports the next exact
command. A landed session removes only clean reachable increment lanes. Neither
case may report `DONE` while tracker execution is suspended.

