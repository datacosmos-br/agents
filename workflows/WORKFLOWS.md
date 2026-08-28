# Personal implementation playbooks

These playbooks guide an operator or personal agent. They are not project
projection content. A project receives only the generic, detected-technology,
and conditionally detected FLEXT skill bundles selected by the projection owner.

## Playbooks

| Work type | File |
|---|---|
| Bug fix | [bug-fix.md](bug-fix.md) |
| Feature | [feature.md](feature.md) |
| Refactor | [refactor.md](refactor.md) |
| Documentation | [docs.md](docs.md) |
| GitOps/Kubernetes | [gitops.md](gitops.md) |

## Entry contract

1. Read repository law and the relevant local docs.
2. Inspect Git remote, branch, integration branch, dirty state, upstream, and
   concurrent WIP.
3. Run `make help` or the repository's declared command discovery surface.
4. Select only commands that the current repository actually declares.
5. Observe the real runtime behavior before changing tests.
6. Work in the existing authorized checkout. While orchestration is suspended,
   create no clone, worktree, workspace, orchestration session, or tracker item;
   create no substitute tracker or ledger, preserve evidence only in separately
   authorized Git/PR/CI, and leave phase closure open.
7. Keep scratch and caches within the storage policy; never use `/tmp` for
   project state.

## Validation contract

Run the smallest native gate that covers each changed slice. Before landing,
run every repository-declared runtime, lint, format, type, test, build,
security, documentation, and generation/fixed-point gate applicable to the
change. Any warning, skip, missing tool, or non-zero exit is red and must be
fixed at its owner.

Every pass claim includes the command, working directory, exit code, decisive
output, commit SHA, and scope. A later edit invalidates earlier evidence for the
affected scope.

## Landing contract

1. Fetch the configured integration branch.
2. If it advanced or diverged, merge `origin/<integration>` into the work
   branch with `--no-ff`; never rebase or force-push.
3. Re-run representative runtime and native gates.
4. Commit explicit paths, push normally, and open or update a PR against the
   configured integration branch.
5. Resolve every conversation, obtain required approval, and require green
   checks.
6. Merge by merge commit.
7. Fast-forward the existing checkout to the integration merge SHA and re-run
   runtime plus native gates there.

A phase is `DONE` only after the approved PR is merged into integration and
its canonical tracker item is closed with evidence. Tracker runtime is
suspended, so the strongest current state is `LANDED_VERIFIED`, never `DONE`.
