---
description: Publishing work — creating a branch, commit, push, or opening a PR. Load when the user asks to commit, push, land, publish, open a pull request, or before any git push.
capsule_summary: |
  Work on a change branch, never on `main` or the integration branch; read the
  base from the repository's own configuration. One git root per PR. The formula
  owns lane creation and teardown — a hand-made worktree or clone is a scope
  expansion the operator must state.

  Checkpoint: scoped `git add`, a `[WIP]` subject, fast-forward push, Draft PR
  with the `WIP` label. `--no-verify` is prohibited and a `[WIP]` commit never
  heads a merge into integration.

  Promotion: one green local round, a non-`[WIP]` commit, green checks, resolved
  conversations and independent approval, then a merge commit — never squash or
  rebase. Revalidate the merge SHA and record post-merge evidence.

  Divergence: merge `origin/<integration>` in with `--no-ff`; never rebase or
  force-push. Retire a branch or worktree only after
  `git merge-base --is-ancestor` exits 0.
metadata:
  aihub.tags: '["decision:plan-00","effective:2026-08-29","route:personal"]'
---

# Branch and PR — integration by merge commit

Work on a change branch, never on `main` or the integration branch. Read the
integration base from the repository's own configuration; never hardcode one or
reuse a sibling's. One git root per PR. Where a tracker is selected, one work
item owns the branch and PR and records head OID, Draft state, gate evidence and
next action at every checkpoint. The formula owns lane creation and teardown:
creating a worktree or clone by hand is a scope expansion the operator must state.

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

**Retirement.** Remove a branch or worktree only after
`git merge-base --is-ancestor <ref> origin/<integration>` exits 0.

A failed check, actionable finding or missing approval keeps the cycle active:
fix and rerun rather than reporting the open PR and moving on.

Control-plane Review transition, Draft aggregation, managed forks, attestation
and the operator-authorized approval row are law too, kept in
`docs/gitflow-landing-detail.md`.
