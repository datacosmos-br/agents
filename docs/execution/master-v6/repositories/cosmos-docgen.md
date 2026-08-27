# Cosmos Docgen runbook

## Repository contract

| Field | Value |
|---|---|
| Remote | `https://github.com/datacosmos-br/cosmos-docgen.git` |
| Integration branch | `dev` |
| Snapshot checkout | `/home/marlonsc/gt/dcdoc/mayor/rig` treated as an independent Git repo |
| Snapshot state | `dev` ahead by one commit; tracked skill/tracker files and dirty data members |
| Active PR | `#71` — setup-uv dependency update, snapshot state `BLOCKED` |
| Final state | `LANDED_VERIFIED_PENDING_TRACKER` |

Read [shared contracts](../01-shared-contracts.md) and
[landing](../03-validation-and-landing.md).

## Mission

Integrate PR #71, resolve the two Python 3.7 security findings at their owner,
regenerate dependency/Actions policy, and install only generic + detected
technology + FLEXT skills as physical project copies.

## Dirty baseline to preserve

The primary checkout contains modified FLEXT skill projections, suspended
tracker metadata, and dirty data repositories. Do not modify or recursively
copy this checkout. The data members are outside this increment unless a native
Cosmos Docgen gate proves a direct dependency.

## Phases

### D1 — Isolate and attribute

1. Capture the ahead commit, dirty diff, member/submodule state, PR #71 base,
   review/checks, worktrees, and branch reachability.
2. Create `.worktrees/<work-id>` from `origin/dev`.
3. Absorb only project-owned, attributable changes. Preserve tracker and dirty
   data-member state in the primary checkout.

Exit: clean isolated lane and no data-member mutation.

### D2 — Reproduce Python findings

1. Record scanner name/version, command, exit, affected lines, and interpreter
   configuration.
2. Prove the Python versions the repository declares and executes.
3. Re-run both Python 3.7 findings against the real supported runtime.
4. If real, fix code at its owner. If a rule/config mismatch, correct that
   owner and prove the finding disappears without `nosemgrep`, ignore, or dead
   compatibility code.

Exit: both findings have reproducible cause and zero unsuppressed result.

### D3 — Dependency policy and PR #71

1. Consume the accepted FLEXT Infra generator policy for Dependabot cooldown,
   uv cooldown, workflow filters, and full-SHA Actions.
2. Regenerate files; never hand-edit generated Dependabot/workflow output.
3. Update PR #71 with current `dev` using `--no-ff` when divergent.
4. Run setup-uv runtime, dependency resolution, lock fixed point, native tests,
   build, and security.
5. Resolve its blocked status and merge by merge commit.

Exit: PR #71 merged and generated files reproduce from owners.

### D4 — Project projection

1. Apply generic, Python, and FLEXT skills from their owners.
2. Remove stale managed copies and reject personal/internal workflows.
3. Confirm physical copies, no local/cross-repo references, and fixed point.

Exit: second apply produces no change.

### D5 — Branch inventory and landing

1. Classify all 90 snapshot branches by protection, reachability, unique work,
   duplication, or uncertainty.
2. Preserve uncertain branches; they block repository closure.
3. Delete only proven reachable obsolete branches after the relevant PR merge.
4. Validate detached `origin/dev` with real generation/runtime and full gates.

## Required validation

- Native help/bootstrap/runtime.
- Python version proof and both finding reproductions.
- Generation fixed point and lock fixed point.
- Full lint, types, tests, build, docs, and security.
- Project projection fixed point.
- PR #71 merge SHA and post-merge `dev` evidence.

## Exit criteria

- PR #71 is merged.
- Python findings are fixed at root cause without suppression.
- Generated policy and projections are converged.
- Every branch has a decisive classification and no increment residue remains.

