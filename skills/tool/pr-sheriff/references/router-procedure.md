# PR Sheriff procedure

# PR Sheriff

Activate only for explicit pull-request triage or landing in one repository
selected by active configuration. Never infer a repository or scan an
organization.

Preflight the repository, integration branch, complete PR inventory, current
tips and base, diff identity, checks, approvals, unresolved threads, merge state,
actor authority, landing method, and any non-derivable current-process GitHub
credential. Read every in-scope PR before classifying any as ready, blocked, or
superseded. A red, missing, stale, or conflicting datum stays blocking.

Inventory the repository's complete CI workflow surface and its generator, when
one exists. Identify the single native CI owner and reject a PR that adds a
duplicate workflow or overlapping CI job, a scanner that scans its own workflow
source, an action not pinned to a full commit SHA, error masking such as
`|| true`, or a workflow that does not execute the repository's declared native
owner. A named check or green job cannot substitute for proving that owner ran.

Use `gh` directly in the operator's current shell. A successful direct command
is credential-readiness evidence; do not reject it based on its authentication
storage backend or demand a duplicate token environment variable. Never extract,
print, migrate, or switch the configured credential or profile.

Before any remote effect, query the exact repository. When GitHub reports it as
private and its owner is `datacosmos-br` or `marlon-costa-dc`, run the bundled
`access` preflight for the required read, push, or admin effect. It requires the
active GitHub account, matching repository permission, an SSH URL for that exact
repository through a non-default declared host alias, and successful
`git ls-remote` through that identity. HTTPS, `github.com`'s generic SSH host,
Git URL rewriting, and alternate account or protocol fallback fail closed.
Public and other-owner repositories do not activate this managed-private
contract. They still require any capability explicitly selected by their own
workflow.

Recommend or execute only the smallest action owned by the repository's current
Git/GitHub lifecycle. Do not copy landing commands here, bypass checks, dismiss
reviews, omit PRs, invoke orchestration/tracker runtime, retry, or switch
repository, credential, integration target, or merge method.

Before an authorized external effect, validate all required gates and approvals.
The first Git, GitHub, check, review, publication, or integration failure
propagates unchanged and produces no success claim. Keep the same PR cycle active:
correct and republish every actionable cause, rerun invalidated checks, resolve
review, obtain approval, merge, and verify the integration SHA. Request owner or
operator action only for a remaining external condition; never triage-and-abandon
an open PR. Remove local residue while preserving the first cause.
