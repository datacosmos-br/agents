---
name: pr-sheriff
description: 'pull requests, review triage, github workflow'
allowed-tools: Bash(gh pr *), Bash(git *)
metadata:
  aihub.tags: '["activation:opt-in","detect:opt-in:pr-sheriff","policy:atomic-effects","policy:causal-subprocess","policy:fail-loud","policy:no-fallback","policy:no-keyring","policy:preflight-before-effects","policy:required-environment","policy:strict-execution","policy:zero-residue","provenance:agents-owned","route:agent","tool:github","updates:manual","usage:on-demand"]'
  author: .agents
  version: 3.0.0
---

# PR Sheriff

Activate only for explicit pull-request triage or landing in one repository
selected by active configuration. Never infer a repository or scan an
organization.

Preflight the repository, integration branch, complete PR inventory, current
tips and base, diff identity, checks, approvals, unresolved threads, merge state,
actor authority, landing method, and any non-derivable current-process GitHub
credential. Read every in-scope PR before classifying any as ready, blocked, or
superseded. A red, missing, stale, or conflicting datum stays blocking.

Recommend or execute only the smallest action owned by the repository's current
Git/GitHub lifecycle. Do not copy landing commands here, bypass checks, dismiss
reviews, omit PRs, invoke orchestration/tracker runtime, use profiles/keyring,
retry, or switch repository, credential, integration target, or merge method.

Before an authorized external effect, validate all required gates and approvals.
The first Git, GitHub, check, review, publication, or integration failure
propagates unchanged and produces no success claim. Keep the same PR cycle active:
correct and republish every actionable cause, rerun invalidated checks, resolve
review, obtain approval, merge, and verify the integration SHA. Request owner or
operator action only for a remaining external condition; never triage-and-abandon
an open PR. Remove local residue while preserving the first cause.
