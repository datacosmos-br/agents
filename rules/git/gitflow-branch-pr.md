---
description: Publishing work — creating a branch, commit, push, or opening a PR. Load when the user asks to commit, push, land, publish, open a pull request, or before any git push.
metadata:
  aihub.tags: '["decision:plan-00","effective:2026-08-29","route:personal"]'
---

# Branch and PR — integration by merge commit

Work on a change branch of the authorized repository, never directly on `main`
or the integration branch. Creating a clone, worktree, workspace, or alternate
checkout is a scope expansion the operator must state explicitly; while
orchestration is suspended it is prohibited.

- The repository owns Git branches, native gates, pull requests, and landing.
- Integration base comes from the repository's own law or configuration; read it
  there for the repository under work. Never hardcode a branch name in universal
  guidance, assume one from another repository, or reuse the base of a sibling
  project.
- One git root per PR; never mix two repositories in one commit or PR.
- When the repository selects its canonical tracker, one active work item owns
  the branch and PR. Record the branch, current head OID, PR identity, Draft/WIP
  state, local gate evidence, and next action in that item at every checkpoint.
  GitHub and tracker state must agree before publication, promotion, landing, or
  closure; divergence blocks the transition and is corrected at the state owner.
- **Draft checkpoint:** stage explicit scoped paths and create a commit whose
  subject starts `[WIP]` whenever a coherent collaboration increment must be
  persisted.
  Commit and push it through the repository-owned WIP path, whose hooks recognize
  typed WIP state and exit before repeating the complete local matrix. Never use
  `--no-verify`. Open or update a Draft PR against integration and apply the
  `WIP` label. No validation is selected for Draft/WIP: local gates,
  attestations, GitHub Actions, CodeQL, Copilot review and review agents all
  remain dormant. WIP commits never merge into integration.
- **Managed fork branches:** when the repository selects managed-fork policy,
  its registered Gas City rig is the project-inventory authority. The fork's
  upstream branch is mirrored exactly into its dedicated mirror branch only by
  the configured automation identity. Humans, including repository admins,
  cannot update, delete, or force-push that branch. The rig-declared integration
  branch accepts changes only through a reviewed PR; no actor bypasses that PR
  requirement.
- **Control-plane Review transition:** a Draft may persist changes to
  `.agents/**`, `.claude/**`, `.codex/**`, `.github/**`, any `AGENTS.md`,
  `CLAUDE.md`, `GEMINI.md`, or `CODEOWNERS`, `rules/**`, `skills/**`,
  `commands/**`, `.beads/**`, `.gc/**`, Make/Mise owners, or declared codegen,
  governance, projection, and attestation manifests. It may enter Review only
  when the actor performing the transition currently has repository `admin`
  permission. The repository-owned guard reads only the base-branch workflow
  and GitHub metadata, never checks out or executes PR-head content. It covers a
  PR opened directly as Review as well as `ready_for_review`; an unauthorized
  transition fails its required check, records the reason, and converts the PR
  back to Draft. Any later head synchronization invalidates the exact-SHA
  receipt and returns the PR to Draft before a new promotion decision.
- **Transparent unbounded aggregation:** a maintained PR may aggregate any finite
  number `N >= 1` of coherent Draft PRs; no configured or implicit cardinality
  limit is permitted. Create it from current integration and merge every exact
  Draft head with `--no-ff`. Record the complete ordered source PR, branch, head
  OID and bead manifest. The agent declares only the maintained PR and source
  PRs; repository automation owns discovery, merges, state, labels, evidence,
  push, comments and closure. On the first successful aggregate push it comments
  every source Draft with the maintained PR and transferred SHA, then closes it.
  The maintained PR may be any PR kind and may remain Draft; no source count or
  PR-kind limit is permitted. When it enters Review, run one complete green
  local validation round covering material tracked changes on its exact
  aggregate head and publish its signed attestation.
  Create a Review promotion commit without `[WIP]`; an empty commit is permitted when
  it is the typed transition into Review. Commit and push normally,
  remove the `WIP` label, convert Draft to Review, require Actions, conversations,
  and independent approval, then merge the exact head by merge commit. Revalidate
  the exact integration merge SHA locally and start the next unit from current
  integration. A red or incomplete round cannot produce either checkpoint or
  promotion.
- The first failing promotion gate exits with its original status and preserves
  the promotion lane at the exact aggregate cursor reached. Do not roll back,
  clean, retry, fall back, attest, or advance Review state. The agent fixes
  forward in that same lane and explicitly invokes promotion again.
- Bind promotion to the branch, PR, and exact head recorded by the work item.
  After landing, record the integration merge SHA and post-merge evidence in the
  same item; close it only when GitHub, Git history, measured runtime, and current
  integrated code agree.
- If integration advanced or diverged, merge `origin/<integration>` into the
  change branch with `--no-ff` and a subject starting `[WIP]`, resolve
  by preserving valid concurrent work, and revalidate. After that clean combined
  round, push through the repository-owned typed WIP path and update the tracker
  head evidence before continuing. `[skip ci]`, `[ci skip]`, `--no-verify`,
  rebase, and force-push are prohibited.
- WIP publication records every validation and attestation as `NOT SELECTED`,
  never as green. Only the non-WIP promotion head may enter integration, and
  it retains the full reviewed-PR and remote-check contract.
- For repositories governed by the managed project workflow, the Review
  promotion automatically runs the matrix and publishes one repository-owned
  signed attestation, bound to the complete aggregate source manifest and the
  exact commit SHA, repository identity, canonical bead, commands, toolchain,
  and results. This is transparent to the agent: the canonical pipeline derives
  the predicate, signs/publishes the tag, and records it in the Bead/PR without
  requiring a hand-authored JSON document or a separate attestation command.
  The promotion bead and Review PR reference the same immutable attestation.
  Review CI verifies signer, SHA, predicate, and complete gate coverage before
  omitting an attested gate; missing, stale, partial, foreign, or invalid proof
  fails closed or runs the uncovered gate as declared by the typed workflow.
  Never describe an unverified local report as a GitHub Artifact Attestation.
  External forks do not inherit this managed trust policy.
- A failed check, actionable review finding, missing approval, or temporarily
  non-mergeable state keeps this landing cycle active. Fix, push, and rerun every
  actionable item; solicit or request help for independent approval only after
  the technical surface is green. Never switch task, phase, or repository merely
  by reporting the open PR state.
- Independent review is mandatory for the promoted landing and never self-granted. When the operator
  states that no independent reviewer exists and authorizes an administrative
  merge, that authorization covers the human approval row only: green checks,
  resolved conversations, merge-commit strategy, and revalidation of the exact
  merge SHA stay mandatory, and the closure record names the approval as
  operator-authorized instead of satisfied.
- Promotion to `main` waits for explicit operator approval.

A phase is `DONE` only after the approved PR is merged into integration and the
canonical tracker item is closed with evidence. Resolve the tracker mode from
the repository's own instructions; while it is explicitly suspended, closure
stays open and no phase may be reported `DONE`.
