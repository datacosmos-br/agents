# PR Sheriff procedure

## PR Sheriff

Activate only for explicit pull-request triage or landing in one repository selected by
active configuration. Never infer a repository or scan an organization.

Preflight the repository, integration branch, complete PR inventory, current tips and
base, diff identity, checks, approvals, unresolved threads, merge state, actor
authority, landing method, and any non-derivable current-process GitHub credential. Read
every in-scope PR before classifying any as ready, blocked, or superseded. A red,
missing, stale, or conflicting datum stays blocking.

Inventory the repository's complete CI workflow surface and its generator, when one
exists. Identify the single native CI owner and reject a PR that adds a duplicate
workflow or overlapping CI job, a scanner that scans its own workflow source, an action
not pinned to a full commit SHA, error masking such as `|| true`, or a workflow that
does not execute the repository's declared native owner. A named check or green job
cannot substitute for proving that owner ran.

Read the repository's active local configuration first and classify its owner,
visibility, association, remote, and integration branch. AI Hub may provide association
metadata, but no AI Hub forge command is a prerequisite for Git or GitHub. Use `gh` and
`git` directly in the operator's current shell. A successful direct command is
credential-readiness evidence; do not demand duplicate token, account, protocol, or
identity configuration. Never extract, print, migrate, or switch the configured
credential or profile.

Before any remote effect, query only the exact configured repository through its current
Git/GitHub configuration. Never create an SSH host alias or read, include, generate, or
edit `~/.ssh/config`; do not rewrite a working remote or invent an alternate account,
identity, or protocol path.

Recommend or execute only the smallest action owned by the repository's current
Git/GitHub lifecycle. Do not copy landing commands here, bypass checks, dismiss reviews,
omit PRs, invoke orchestration/tracker runtime, retry, or switch repository, credential,
integration target, or merge method.

Before an authorized external effect, validate all required gates and approvals. The
first Git, GitHub, check, review, publication, or integration failure propagates
unchanged and produces no success claim. Keep the same PR cycle active: correct and
republish every actionable cause, rerun invalidated checks, resolve review, obtain
approval, merge, and verify the integration SHA. Request owner or operator action only
for a remaining external condition; never triage-and-abandon an open PR. Remove local
residue while preserving the first cause.
