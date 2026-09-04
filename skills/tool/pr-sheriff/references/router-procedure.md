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

Read the repository's active local configuration first and classify its owner,
visibility, and selected access contract without a remote command. Only when
that configuration explicitly selects AI Hub's managed-private contract, resolve
the configured workspace through `ai-hub forge-resolve --workspace` and validate
its configured account and Git identity with `ai-hub forge-doctor`. A public or
other-owner repository does not run either command. Use `gh` directly in the
operator's current shell afterward when GitHub access is selected. A successful
direct command is credential-readiness evidence; do not reject it based on its
authentication storage backend or demand a duplicate token environment variable.
Never extract, print, migrate, or switch the configured credential or profile.

Before any remote effect, query only the exact configured repository through its
selected capability. When local configuration selects the AI Hub managed-private
contract and GitHub confirms the repository is private, require its resolved active account,
matching repository permission, the exact `git@github.com:owner/repo.git` origin,
repository-local `core.sshCommand` selecting the declared identity, and successful
`git ls-remote` through that configuration. Never create an SSH host alias or
read, include, generate, or edit `~/.ssh/config`. HTTPS, Git URL rewriting, and
alternate account, identity, or protocol fallback fail closed.
Public and other-owner repositories do not activate this managed-private
contract, do not invoke AI Hub forge preflight, and still require only the
capabilities explicitly selected by their own workflow.

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
