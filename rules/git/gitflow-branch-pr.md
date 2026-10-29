---
description:
  Publishing work — creating a branch, commit, push, or opening a PR. Load when the user
  asks to commit, push, land, publish, open a pull request, or before any git push.
capsule_summary: |
  Follow the operator-declared checkout and integration route. Fixes and hotfixes
  reach integration in the same phase, never as deferred patches. The base is
  what the repository declares today: read it per repository, never assume or
  reuse one. `origin/<base>` is a cache: fetch it before any ancestry
  proof that authorizes deletion. One git root per PR; placement follows the
  active/manual Gas City boundary.
  Checkpoint: complete green slice, scoped add, fast-forward push and reviewed PR.
  Incomplete work may be published only to explicitly authorized preservation refs,
  never the working or integration branch. Preservation is not delivery.
  Promotion: green local round, non-`[WIP]` commit, green checks, resolved review,
  independent approval, merge commit — never squash or rebase. Revalidate the merge
  SHA with post-merge evidence.
  Divergence: merge the integration base in with `--no-ff`; never rebase or
  force-push.
  Retire only authorized, invocation-owned disposable lanes after ownership and
  fresh ancestry proof. Never delete the adopted primary/shared checkout or
  integration branch because one task ends.
metadata:
  aihub.tags: '["decision:ADR-0025","effective:2026-10-29","route:personal"]'
---

# Branch and PR — integration by merge commit

Follow the operator-declared checkout and integration route. Fixes and hotfixes must
be applied through the declared integration branch in the current phase; a correction
left on a working branch is not an integrated delivery. An explicit integration-branch
instruction overrides the default change-branch route. Promotion to `main` still needs
explicit approval. One git root per PR.
Where a tracker is selected, one work item owns the branch and PR and records head OID,
Draft state, gate evidence and next action at every checkpoint. Lane creation and
teardown follow `rules/coordination/gascity.md`: active orchestration uses its owner.
Preserve the operator-selected existing checkout and compatible concurrent work; never
require a clean/stable tree or create another worktree to evade it. Do not reactivate
suspended orchestration to provision a lane. Creating another checkout or publishing
work still requires the applicable operator authorization.

**The base is read, never assumed.** The integration base is whatever the repository
and the operator currently declare; a forge default is not automatically the integration
branch. Never hardcode one, carry one from
a sibling, or infer one from a local ref. Resolve it per repository at preflight, and
preserve the command and output that proved it.

**A ref is not evidence until it is fresh.** `origin/<base>` is a local cache. A
truncated fetch refspec, a stale ref, or a base that simply moved makes every ancestry
proof answer about the past, and `merge-base --is-ancestor` then reports "integrated"
for work that is not. Fetch the base from the remote immediately before any proof that
authorizes deletion, and confirm the refspec actually covers it. A deletion authorized
by a stale ref destroys work and is the same class of failure as deleting without proof
at all.

**Checkpoint.** Complete the slice, prove its public runtime and pass its declared
native gates before committing scoped paths, pushing fast-forward and opening or
updating its PR. Operator order 2026-10-24, recorded in
`operator-order-2026-10-24-no-incomplete-pushes`, supersedes the earlier checkpoint
instruction to publish incomplete `[WIP]` heads on the working branch. Incomplete work
may be published only to an explicitly authorized preservation ref, never to a working
or integration branch or a PR. Preservation grants no landing, validation or completion
claim. A Draft state does not waive local acceptance; unselected external checks remain
`NOT SELECTED`, never green. `--no-verify` is prohibited.

**Promotion.** One green local round on the exact head, then a non-`[WIP]` commit,
remove the label, Draft to Review, require green checks, resolved conversations and
independent approval — never self-granted. Merge by merge commit; squash and rebase are
prohibited. Revalidate the merge SHA, record it and post-merge evidence, and close only
when GitHub, Git history, runtime and integrated code agree. Promotion to `main` waits
for explicit operator approval.

**Divergence.** Merge `origin/<integration>` into the lane with `--no-ff`, preserve valid
concurrent work and revalidate before publishing. An in-progress integration is not a
green checkpoint. `[skip ci]`, `--no-verify`, rebase and force-push are prohibited.

**Red base.** When the base already fails its own gate, adopt those defects in the same
PR and cite the owning commit. Never narrow a gate or exclude a failing path to look
green on a red base.

**Retirement closes disposable lanes, not adopted workspaces.** Carry authorized
work through integration and retire its eligible invocation-owned lane in that cycle.
Never infer deletion authority over the primary/shared checkout, integration branch
or another actor's context. Preserve all WIP. Ownership and recovery proof must
precede removal. Require `git merge-base --is-ancestor <ref> origin/<integration>`
against a freshly fetched base; ancestry alone is insufficient.

A failed check, actionable finding or missing approval keeps the cycle active: fix and
rerun rather than reporting the open PR and moving on.

Control-plane Review transition, Draft aggregation, managed forks, attestation and the
operator-authorized approval row are law too, kept in `docs/gitflow-landing-detail.md`.

The 2026-10-29 reconciliation preserves the 2026-10-24 green-checkpoint order
without reviving its older ban on diagnostic gates for incomplete work. The
operator's current publication authorization persists within its declared scope;
it never waives current-SHA CI, review, integration or required runtime proof.
