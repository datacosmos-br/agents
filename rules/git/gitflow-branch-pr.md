---
description: Publishing work — creating a branch, commit, push, or opening a PR. Load when the user asks to commit, push, land, publish, open a pull request, or before any git push.
capsule_summary: |
  Work on a change branch, never on `main` or the integration branch. The base is
  whatever the repository itself declares today — read it per repository, never
  assume or reuse one. `origin/<base>` is a cache: fetch it from the remote
  before any ancestry proof that authorizes deletion, or the proof answers about
  the past and destroys work. One git root per PR. The formula owns lane creation
  and teardown — a hand-made worktree or clone is a scope expansion the operator
  must state.

  Checkpoint: scoped `git add`, a `[WIP]` subject, fast-forward push, Draft PR
  with the `WIP` label. `--no-verify` is prohibited and a `[WIP]` commit never
  heads a merge into integration.

  Promotion: one green local round, a non-`[WIP]` commit, green checks, resolved
  conversations and independent approval, then a merge commit — never squash or
  rebase. Revalidate the merge SHA and record post-merge evidence.

  Divergence: merge `origin/<integration>` in with `--no-ff`; never rebase or
  force-push.

  Retirement closes the cycle and is not optional: a lane opened is carried to
  integration and retired in the same cycle — merge, push, PR, merge, then delete
  the local branch, the remote branch and the worktree. Retire only after
  `git merge-base --is-ancestor` exits 0 against a just-fetched base.
metadata:
  aihub.tags: '["decision:plan-00","effective:2026-08-29","route:personal"]'
---

# Branch and PR — integration by merge commit

Work on a change branch, never on `main` or the integration branch. One git root
per PR. Where a tracker is selected, one work item owns the branch and PR and
records head OID, Draft state, gate evidence and next action at every checkpoint.
The formula owns lane creation and teardown: creating a worktree or clone by hand
is a scope expansion the operator must state.

**The base is read, never assumed.** The integration base is whatever the
repository itself currently declares — its forge default branch. Never hardcode
one, carry one from a sibling, or infer one from a local ref. Resolve it per
repository at preflight, and preserve the command and output that proved it.

**A ref is not evidence until it is fresh.** `origin/<base>` is a local cache. A
truncated fetch refspec, a stale ref, or a base that simply moved makes every
ancestry proof answer about the past, and `merge-base --is-ancestor` then reports
"integrated" for work that is not. Fetch the base from the remote immediately
before any proof that authorizes deletion, and confirm the refspec actually
covers it. A deletion authorized by a stale ref destroys work and is the same
class of failure as deleting without proof at all.

**Checkpoint.** Stage scoped paths, commit with a `[WIP]` subject, push
fast-forward, open or update a Draft PR against integration, apply the `WIP`
label. Draft selects no validation — gates and attestations record `NOT SELECTED`,
never green. `--no-verify` is prohibited, and a `[WIP]` commit never heads a merge
into integration.

**Promotion.** One green local round on the exact head, then a non-`[WIP]` commit,
remove the label, Draft to Review, require green checks, resolved conversations
and independent approval — never self-granted. Merge by merge commit; squash and
rebase are prohibited. Revalidate the merge SHA, record it and post-merge
evidence, and close only when GitHub, Git history, runtime and integrated code
agree. Promotion to `main` waits for explicit operator approval.

**Divergence.** Merge `origin/<integration>` into the lane with `--no-ff` and a
`[WIP]` subject, preserve valid concurrent work, revalidate. `[skip ci]`,
`--no-verify`, rebase and force-push are prohibited.

**Red base.** When the base already fails its own gate, adopt those defects in the
same PR and cite the owning commit. Never narrow a gate or exclude a failing path
to look green on a red base.

**Retirement closes the cycle; it is not optional.** A lane is carried to the
integration branch and retired in the same cycle it opened: merge integration in,
resolve fix-forward, push, open the PR, merge it, then delete the local branch,
its remote branch and its worktree. Leaving a lane published-but-unmerged, or
merged-but-not-retired, is the accumulation this rule exists to prevent. Remove a
branch or worktree only after `git merge-base --is-ancestor <ref>
origin/<integration>` exits 0 against a base just fetched from the remote.

A failed check, actionable finding or missing approval keeps the cycle active:
fix and rerun rather than reporting the open PR and moving on.

Control-plane Review transition, Draft aggregation, managed forks, attestation
and the operator-authorized approval row are law too, kept in
`docs/gitflow-landing-detail.md`.
