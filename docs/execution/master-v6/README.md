# Master v6 execution package

Six repositories must land independently on their configured integration
branches. Gas Town, Beads, and Dolt are suspended for this increment. Git and
GitHub are the execution path.

This directory is the durable handoff for new sessions. Start here, read the
shared contracts, then open only the runbook for the repository you will work
on.

## Authority

The newest operator instructions win over older plans, tracker text, skills,
and generated documentation. This package supersedes the Poolside plans and
conversation-only versions of master plans v1-v5 for this increment.

The operator fixed these decisions:

- Do not invoke, modify, inspect operationally, or depend on Gas Town.
- Do not invoke Beads or Dolt during the pause.
- Preserve existing Gas Town/Dolt audit code, but keep it dormant and outside
  default gates.
- Use Git and GitHub directly.
- Use persistent repository-local Git worktrees. Do not use `/tmp`, loose
  clones, symlinks, stash, rebase, force-push, or destructive reset.
- Treat existing dirty work as owned input. Preserve and absorb it
  semantically; never discard it.
- Merge the integration base into each work branch with `--no-ff` when the
  branch diverges, then validate before the PR.
- Merge PRs by merge commit into the configured integration branch.
- A technically landed increment is recorded as
  `LANDED_VERIFIED_PENDING_TRACKER`, never `DONE`, while tracker execution is
  suspended.

## Reading order

1. [Authority and scope](00-authority-and-scope.md)
2. [Shared contracts](01-shared-contracts.md)
3. [Execution graph](02-execution-graph.md)
4. [Validation and landing](03-validation-and-landing.md)
5. [Session protocol](04-session-protocol.md)
6. One repository runbook:
   - [Agents](repositories/agents.md)
   - [AI Hub](repositories/ai-hub.md)
   - [Cosmos Docgen](repositories/cosmos-docgen.md)
   - [Invest](repositories/invest.md)
   - [FLEXT Infra](repositories/flext-infra.md)
   - [CCS](repositories/ccs.md)

## Repository snapshot

Snapshot captured on 2026-08-27. Re-query GitHub and Git at session start.
Counts are evidence, not constants.

| Repository | Integration | Open PRs | Remote branches | Runbook |
|---|---|---:|---:|---|
| `marlon-costa-dc/agents` | `dev` | 1 | 3 | [agents.md](repositories/agents.md) |
| `datacosmos-br/ai-hub` | `dev` | 9 | 29 | [ai-hub.md](repositories/ai-hub.md) |
| `datacosmos-br/cosmos-docgen` | `dev` | 1 | 90 | [cosmos-docgen.md](repositories/cosmos-docgen.md) |
| `marlonsc/invest` | `main` | 0 | 10 | [invest.md](repositories/invest.md) |
| `flext-sh/flext-infra` | `0.12.0-dev` | 30 | 88 | [flext-infra.md](repositories/flext-infra.md) |
| `marlon-costa-dc/ccs` | `main` | 0 | 14 | [ccs.md](repositories/ccs.md) |

## Status vocabulary

| State | Meaning |
|---|---|
| `NOT_STARTED` | No isolated lane has been verified. |
| `ISOLATED` | Worktree/branch and baseline evidence exist. |
| `IN_PROGRESS` | Owner changes are being made. |
| `BLOCKED` | A required runtime, gate, review, or external service failed. |
| `PR_OPEN` | PR targets the configured integration branch. |
| `MERGED` | GitHub reports a merge commit on the integration branch. |
| `LANDED_VERIFIED_PENDING_TRACKER` | Post-merge runtime and gates passed; tracker remains suspended. |

No session may translate `BLOCKED` into green, treat an expected error as a
pass, or report `DONE` from local tests, a commit, a push, or an open PR.
