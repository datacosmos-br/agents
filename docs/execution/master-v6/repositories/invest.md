# Invest runbook

## Repository contract

| Field | Value |
|---|---|
| Remote | `https://github.com/marlonsc/invest.git` |
| Integration branch | `main` |
| Snapshot checkout | `/home/marlonsc/gt/invest/mayor/rig` treated as an independent Git repo |
| Snapshot state | `main` ahead by one commit; tracker metadata and a large untracked `.agents` projection dirty |
| Open PRs | 0 |
| Remote branches | 10 |
| Final state | `LANDED_VERIFIED_PENDING_TRACKER` |

Read [shared contracts](../01-shared-contracts.md) and
[landing](../03-validation-and-landing.md).

## Mission

Replace the current unreviewed `.agents` tree with a deterministic physical
projection, apply generated dependency/security policy, classify all remote
branches, and land the result on `main` through a PR.

## Dirty baseline to preserve

The primary checkout contains:

- one local commit ahead of `origin/main`;
- suspended tracker metadata;
- untracked `.agents/commands`, `.agents/rules`, skill directories, and a
  projection manifest.

Treat the untracked projection as evidence of the old policy, not as authority.
Do not delete or overwrite it in the primary checkout. Compare its contents
with the new owner output and reproduce the accepted result in the isolated
lane.

## Phases

### I1 — Isolate and analyze the projection

1. Capture the ahead commit, dirty/untracked tree, branch list, worktrees,
   integration SHA, and reachability.
2. Create `.worktrees/<work-id>` from `origin/main`.
3. Determine whether the ahead commit belongs to this increment; cherry-pick
   only a fully attributable commit.
4. Inventory the existing projected skills by distribution class and compare
   them with the Agents catalog.

Exit: old projection is preserved and every accepted delta has an owner.

### I2 — Generate the correct project surface

1. Detect Python and FLEXT from repository markers/dependencies.
2. Apply only generic + Python + FLEXT skills as physical copies.
3. Exclude personal workflows, suspended skills, ECC, SkillShare, and internal
   repository workflows.
4. Validate no absolute local path, symlink, or cross-repo reference exists.
5. Apply twice and require zero second-pass diff.

Exit: one deterministic projection manifest and physical tree.

### I3 — Dependency and security owners

1. Consume accepted generated cooldown/Actions policy from FLEXT Infra.
2. Regenerate Dependabot and related workflows through the owner.
3. Resolve uv with the seven-day cooldown and prove lock fixed point.
4. Run deterministic manifest inventory, Python audits, Semgrep, Snyk,
   Gitleaks, Actions checks, and project-native scanners.

Exit: every tracked manifest is scanned and generated policy is converged.

### I4 — Branch reconciliation

Classify the 10 snapshot remote branches:

- integration/protected: retain;
- reachable and inactive: remove after proof;
- unique work: clean branch, runtime, gates, PR;
- duplicate: remove only after substitute SHA reaches `main`;
- uncertain: preserve and block closure.

Exit: no uncertain branch and every retained unique change has a PR.

### I5 — Landing

1. Merge current `origin/main` into the work branch with `--no-ff` when
   divergent.
2. Run real application/config runtime, then full native gates.
3. Open PR against `main`, resolve checks/reviews, and merge by merge commit.
4. Validate detached `origin/main` and remove clean reachable lanes.

## Required validation

- Project-native runtime and complete Make/quality gates.
- Projection and generation fixed points.
- Python/security scanner matrix with manifest coverage.
- Branch reachability evidence.
- Post-merge runtime at the integration SHA.

## Exit criteria

- `main` contains the approved generated projection and dependency policy.
- The original dirty checkout was not discarded or rewritten.
- All 10 snapshot branches are decisively classified.
- No increment worktree/branch, stale managed projection, or scanner omission
  remains.

