# Authority and scope

## Goal

Land the agents governance, credential, Waza, skill, projection, storage,
security, and repository-cohesion increment across six repositories without an
operational dependency on Gas Town, Beads, or Dolt.

## In scope

- `agents`: governance CLI, skill authority, Waza, projections, temp/cache,
  security gates, and PR #4.
- `ai-hub`: credential/config owners, generated consumers, open PR
  reconciliation, and project projections.
- `cosmos-docgen`: generated dependency policy, Python security findings,
  Actions, PR #71, and project projections.
- `invest`: generated dependency policy, project projections, dirty work, and
  branch inventory.
- `flext-infra`: generator owners, dependency cooldown policy, security,
  scratch boundary, and PR/branch consolidation.
- `ccs`: proxy runtime, local package delivery, test parity, release-policy
  correction without a release, and project projections.

## Out of scope

- The Gas Town repository, service, sessions, hooks, rigs, crews, polecats,
  refinery, routes, databases, security findings, and PRs.
- Tracker recovery, Beads migration, bead creation/update/closure, Dolt push,
  listener validation, or any operation against port 3307.
- Promotion beyond each repository's integration branch.
- Tags, public releases, package publication, and changes to unrelated secrets.
- New public interfaces beyond those listed in
  [Shared contracts](01-shared-contracts.md).

## Non-negotiable filesystem rules

- Worktrees live under `<repo>/.worktrees/<work-id>` on persistent storage.
- Existing `.agents` and CCS lanes remain valid isolated lanes and must not be
  duplicated without cause.
- `.worktrees/` belongs in the repository-local Git exclude, not a generated
  project file.
- `/tmp` is limited to small bounded OS primitives. It is not a workspace,
  clone, backup, report store, cache root, or build root.
- No symlink or cross-repository content reference may be introduced.
- Linux copy operations use `cp --archive --reflink=auto` when the filesystem
  supports reflinks.
- Live process, valid lock, dirty Git tree, database, symlink, and unknown
  content are preserved.

## Git authority for this increment

The operator authorized direct Git/GitHub execution while Gas Town is paused.
That authority is narrow:

- create repository-local worktrees and work branches;
- fetch and merge the configured integration branch with `--no-ff`;
- commit, push normally, create/update PRs, respond to reviews, and merge by
  merge commit;
- delete a branch only after reachability proof and use `git branch -d`;
- remove a worktree only after it is clean, merged, and post-merge validated.

It does not authorize rebase, force-push, direct integration-branch edits,
`reset --hard`, global stash, loose clone, squash merge, or branch deletion by
guesswork.

## Manual evidence ledger

Canonical ledger during the pause:

```text
${XDG_STATE_HOME:-$HOME/.local/state}/agents/ledger/agents-audit-ledger.jsonl
```

Each state-changing event records:

```json
{
  "time": "RFC3339",
  "work_id": "stable repository-scoped ID",
  "repository": "owner/name",
  "event": "state transition",
  "files": ["paths"],
  "intent": "why the state changed",
  "proof": {"command": "...", "exit": 0, "decisive_output": "..."},
  "phase_status": "IN_PROGRESS"
}
```

Never place secret values, fingerprints, credentials, or complete environments
in the ledger.

## Stop conditions

Stop the affected repository lane and record the exact failure when:

- a command attempts to invoke the suspended runtime;
- a required secret is missing or rejected;
- runtime, scanner, test, review, or branch protection is red;
- a public interface outside the approved list becomes necessary;
- dirty work cannot be attributed without risking another actor's work;
- a branch cannot be proven merged, unique, duplicated, or obsolete;
- a cleanup candidate has an owner, liveness, or content ambiguity.

