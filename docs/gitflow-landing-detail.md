# GitFlow landing — operational detail

Companion to `rules/git/gitflow-branch-pr.md`. The rule states the enforceable
contract and is delivered in every session capsule, which carries a hard size
budget; this document holds the operational detail that does not fit there and
does not need to be restated at every prompt.

Nothing here is new. It is the text that lived inside the rule until `ag-qio`
moved it, preserved so the compaction removed length, not law.

## Draft validation is not selected

No validation is selected for Draft/WIP: local gates, attestations, GitHub
Actions, CodeQL, Copilot review and review agents all remain dormant. WIP commits
never merge into integration.

WIP publication records every validation and attestation as `NOT SELECTED`, never
as green. Only the non-WIP promotion head may enter integration, and it retains
the full reviewed-PR and remote-check contract.

## Control-plane Review transition

A Draft may persist changes to `.agents/**`, `.claude/**`, `.codex/**`,
`.github/**`, any `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, or `CODEOWNERS`,
`rules/**`, `skills/**`, `commands/**`, `.beads/**`, `.gc/**`, Make/Mise owners,
or declared codegen, governance, projection, and attestation manifests. It may
enter Review only when the actor performing the transition currently has
repository `admin` permission.

The repository-owned guard reads only the base-branch workflow and GitHub
metadata; it never checks out or executes PR-head content. It covers a PR opened
directly as Review as well as `ready_for_review`. An unauthorized transition
fails its required check, records the reason, and converts the PR back to Draft.
Any later head synchronization invalidates the exact-SHA receipt and returns the
PR to Draft before a new promotion decision.

## Transparent unbounded aggregation

A maintained PR may aggregate any finite number `N >= 1` of coherent Draft PRs;
no configured or implicit cardinality limit is permitted. Create it from current
integration and merge every exact Draft head with `--no-ff`. Record the complete
ordered source PR, branch, head OID and bead manifest.

The agent declares only the maintained PR and source PRs; repository automation
owns discovery, merges, state, labels, evidence, push, comments and closure. On
the first successful aggregate push it comments every source Draft with the
maintained PR and transferred SHA, then closes it. The maintained PR may be any
PR kind and may remain Draft; no source count or PR-kind limit is permitted.

When it enters Review, run one complete green local validation round covering
material tracked changes on its exact aggregate head and publish its signed
attestation. Create a Review promotion commit without `[WIP]`; an empty commit is
permitted when it is the typed transition into Review. A red or incomplete round
cannot produce either checkpoint or promotion.

The first failing promotion gate exits with its original status and preserves the
promotion lane at the exact aggregate cursor reached. Do not roll back, clean,
retry, fall back, attest, or advance Review state. Fix forward in that same lane
and invoke promotion again explicitly.

## Managed fork branches

When the repository selects managed-fork policy, its registered Gas City rig is
the project-inventory authority. The fork's upstream branch is mirrored exactly
into its dedicated mirror branch only by the configured automation identity.
Humans, including repository admins, cannot update, delete, or force-push that
branch. The rig-declared integration branch accepts changes only through a
reviewed PR; no actor bypasses that PR requirement.

## Signed attestation on managed promotion

For repositories governed by the managed project workflow, the Review promotion
automatically runs the matrix and publishes one repository-owned signed
attestation, bound to the complete aggregate source manifest and the exact commit
SHA, repository identity, canonical bead, commands, toolchain, and results.

This is transparent to the agent: the canonical pipeline derives the predicate,
signs and publishes the tag, and records it in the bead and PR without a
hand-authored JSON document or a separate attestation command. The promotion bead
and Review PR reference the same immutable attestation.

Review CI verifies signer, SHA, predicate, and complete gate coverage before
omitting an attested gate; missing, stale, partial, foreign, or invalid proof
fails closed or runs the uncovered gate as declared by the typed workflow. Never
describe an unverified local report as a GitHub Artifact Attestation. External
forks do not inherit this managed trust policy.

## Independent approval when no reviewer exists

Independent review is mandatory for the promoted landing and never self-granted.
When the operator states that no independent reviewer exists and authorizes an
administrative merge, that authorization covers the human approval row only:
green checks, resolved conversations, merge-commit strategy, and revalidation of
the exact merge SHA stay mandatory, and the closure record names the approval as
operator-authorized instead of satisfied.
