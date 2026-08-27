# Validation and landing

## Evidence format

Every claimed pass records:

- repository and commit SHA;
- command and working directory;
- exit code;
- decisive output such as test count, scan count, response status, or fixed
  point;
- artifact path when applicable;
- state transition.

Do not record full environments, tokens, fingerprints, or raw scanner payloads
that contain secrets.

## Runtime-before-gates rule

Run the smallest representative real behavior before broad tests:

- credentials: login/interactive shells, `auto-exec`, Mise, GitHub API, proxy;
- Waza: selected model, tool call, artifact, and failure classification;
- migration skill: one representative atomic conversion;
- projection: one real project from each applicable profile;
- dependency policy: one real resolution/update and lock fixed point;
- CCS: Node/Bun transport and proxy path.

If runtime fails, stop that lane. Do not use unit tests to override a failed
runtime result.

## Shared validation matrix

| Area | Required proof |
|---|---|
| Secrets | No 401; aliases resolve from one physical source; no secret output. |
| Temp | Concurrent isolation; signals stop owned group; safe fixtures preserved. |
| Skills | 76 valid routers; token budgets; short descriptions; no ECC/SkillShare. |
| Waza | 228 semantic scenarios; preflight; artifact validation; no false green. |
| Projection | Personal/generic/technology/FLEXT separation; physical fixed point. |
| Security | Deterministic manifest inventory; all applicable scanners exit 0. |
| CI | Native offline pipeline passes from a clean isolated lane. |
| Docs | Command/help checks match current interfaces; links resolve. |

Repository-specific commands belong in each runbook. A new session must run
`make help` or the repository's equivalent before choosing gates.

## PR procedure

1. Fetch remotes and record the current integration SHA.
2. Confirm the worktree is clean except for intended changes.
3. If integration advanced, run `git merge --no-ff origin/<integration>`.
4. Resolve conflicts by preserving both valid owner changes.
5. Run representative runtime.
6. Run every native test, lint, type, build, security, generation, and fixed
   point gate.
7. Commit specific files and push normally.
8. Open or update the PR against the configured integration branch.
9. Resolve every conversation and required check. Billing failures, quota
   errors, skipped reviews, and neutralized gates are not approval.
10. Merge through GitHub with “Create a merge commit.”

## Post-merge procedure

1. Fetch the integration branch and verify the GitHub merge SHA is reachable.
2. Create `<repo>/.worktrees/<work-id>-postmerge` detached at
   `origin/<integration>`.
3. Rebuild/bootstrap from clean state.
4. Repeat representative runtime and the native complete gate.
5. Record the SHA and outputs in the ledger.
6. Remove the detached validation worktree.
7. Delete the local work branch with `git branch -d` only when reachable.
8. Delete a remote branch only when policy permits and reachability is proven.

## Branch protection

For each integration branch:

- require pull request;
- require one approval;
- require native checks;
- require conversation resolution;
- block force-push and deletion;
- enable merge commits;
- disable squash and rebase merge;
- disable linear-history requirement.

Record the ruleset/rule IDs and effective repository settings. Do not claim the
policy is active from a configuration request alone; read it back from GitHub.

## Final exit

The package is landed only when all repository runbooks satisfy their exit
criteria, every owner/consumer projection is at fixed point, no increment
branch/worktree remains, and post-merge runtime is green.

The ledger state is `LANDED_VERIFIED_PENDING_TRACKER`. Do not use `DONE` while
tracker execution is suspended.
