# FLEXT Infra runbook

## Repository contract

| Field | Value |
|---|---|
| Remote | `https://github.com/flext-sh/flext-infra.git` |
| Integration branch | `0.12.0-dev` |
| Active lane | `/home/marlonsc/flext-work/flext-infra`, branch `fix/project-scratch-runner-boundary` |
| Active PR | `#436` for the active lane |
| Snapshot state | Lane clean; 30 open PRs; 88 remote branches |
| Special PR | `#47` targets `0.20.0-dev` from `0.12.0-dev` and must not promote |
| Final state | `LANDED_VERIFIED_PENDING_TRACKER` |

Read [shared contracts](../01-shared-contracts.md) and
[landing](../03-validation-and-landing.md).

## Mission

Make FLEXT Infra the sole generator owner for dependency cooldown, Actions,
project templates, and scratch boundaries while preserving FLEXT semantic
skills at their canonical FLEXT owner. Reconstruct useful PR work on
`0.12.0-dev`, remove checkpoint/rescue residue only after reachability proof,
and propagate accepted generated policy to consumers.

## Owner boundary

- FLEXT Infra owns templates, generators, policy schemas, and generated-file
  checks.
- The FLEXT semantic source owns framework skill meaning.
- `.agents` owns generic/personal/technology classification.
- Consumer repositories receive physical generated/copied outputs.

Do not duplicate semantic FLEXT skill ownership in FLEXT Infra.

## Phases

### F1 — Establish the live lane and PR graph

1. Re-query all open PRs, bases, heads, reviews, checks, branches, and current
   worktree reachability.
2. Continue the existing clean `fix/project-scratch-runner-boundary` lane for
   PR #436; do not create a duplicate lane.
3. Build a graph grouping PRs into functional, dependency, checkpoint, backup,
   rescue, WIP, duplicate, and uncertain classes.
4. Record which generated surfaces and consumers each functional PR affects.

Exit: all 30 current PRs and 88 branches have preliminary ownership/class.

### F2 — Scratch and storage boundary

1. Finish PR #436 at the runtime allocation owner.
2. Enforce project-local, per-run scratch and explicit cache/state roots.
3. Remove `/tmp` workspace/cache patterns from generators, hooks, tests, and
   docs.
4. Test concurrent Python/Go/Node/Rust/Java consumers and safe cleanup.
5. Run native infra generators twice and verify no generated drift.

Exit: PR #436 runtime and full pipeline green with bounded residue.

### F3 — Dependency and Actions policy

Set at the generator owner:

```yaml
cooldown:
  default-days: 7
```

```toml
[tool.uv]
exclude-newer = "7 days"
```

Then:

1. Ensure cooldown affects version updates only, not security updates.
2. Regenerate lockfiles so uv records the effective cutoff timestamp.
3. Pin third-party Actions by full SHA.
4. Include `.mise.toml`, owner configs, and generators in workflow path
   filters.
5. Add generator tests for exact output and second-run fixed point.

Exit: owner tests and representative consumer regeneration pass.

### F4 — PR reconstruction

- Functional PRs are rebuilt or updated on `0.12.0-dev` with attributable
  commits and native gates.
- Never merge `checkpoint/*`, `backup/*`, `rescue/*`, or `wip/*` branches as a
  whole.
- Extract unique hunks only after owner and runtime proof.
- PR #47 does not promote to `0.20.0-dev`. Extract still-valid corrections to a
  clean `0.12.0-dev` branch, land them, then close #47 as superseded with the
  replacement SHA.
- A dirty/unstable PR cannot be closed until its unique work is merged or proven
  duplicate.

Exit: every PR is merged, superseded by a reachable SHA, or explicitly blocked
  as uncertain.

### F5 — Security and consumer propagation

1. Run deterministic manifest inventory and every applicable scanner.
2. Fix findings at generator/library owners; no suppression.
3. Regenerate AI Hub, Cosmos Docgen, and Invest from the accepted owner commit.
4. Validate consumer runtime before tests and lock/projection fixed points.

Exit: consumers reproduce generated policy without manual edits.

### F6 — Landing and branch cleanup

1. Merge current `origin/0.12.0-dev` into surviving work branches with
   `--no-ff` when divergent.
2. Run runtime, full native gates, generation, and security.
3. Merge approved PRs by merge commit.
4. Validate detached `origin/0.12.0-dev` after dependency-sensitive batches.
5. Delete only clean reachable branches/worktrees; uncertain state blocks exit.

## Required validation

- Repository-native help, generator, tests, lint, types, build, and security.
- Scratch concurrency and residue measurements.
- Generator and lock fixed points.
- Representative AI Hub, Cosmos Docgen, and Invest regeneration/runtime.
- PR/branch reachability table with replacement SHAs.

## Exit criteria

- `0.12.0-dev` owns the accepted scratch and dependency policies.
- PR #47 did not promote the branch and has a reachable substitute if closed.
- All 30 snapshot PRs and 88 branches are decisively resolved.
- Consumer projections regenerate cleanly and no increment residue remains.

