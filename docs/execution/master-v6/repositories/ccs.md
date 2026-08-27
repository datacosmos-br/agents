# CCS runbook

## Repository contract

| Field | Value |
|---|---|
| Remote | `https://github.com/marlon-costa-dc/ccs.git` |
| Integration branch | `main` |
| Active lane | `/home/marlonsc/gt/ccs/crew/agents_audit`, branch `crew/agents_audit` |
| Snapshot state | 18 files changed, 618 insertions, 165 removals; no open PR |
| Remote branches | 14 |
| Final state | `LANDED_VERIFIED_PENDING_TRACKER` |

The lane path is historical placement only. Treat it as an independent Git
worktree and never call its orchestration owner. Read
[shared contracts](../01-shared-contracts.md) and
[landing](../03-validation-and-landing.md).

## Mission

Deliver a hermetic CCS/CLIProxy runtime for Waza, correct the fork's package and
workflow behavior, finish full CI parity, install a physical local package by
commit digest, project the correct project skills, and reconcile all remote
branches.

## Dirty baseline and proven results

Changes currently cover release workflows, release config, package scripts,
postinstall, test buckets, proxy runtime matrix, browser MCP, fixtures, and
tests. `AGENTS.md` was converted from a symlink to a physical file and mirrored
with `CLAUDE.md`.

Previous evidence, which must be re-run against the final commit:

- fast validation bucket: 398 selected files passed;
- Node 18/22/26 and Bun runtime matrix: 4 passed;
- targeted postinstall and Browser MCP regressions: 34 passed;
- full CI parity remains red;
- concurrent state-lock test most recently exited 127 after resource-related
  failures; root cause is unresolved;
- replay was changed to wait for completion and passed its targeted test.

## Phases

### C1 — Reconcile the dirty lane

1. Capture diff, current base, upstream, worktrees, branches, and package/tool
   versions.
2. Map each changed file to proxy runtime, package delivery, browser contract,
   test hermeticity, or unrelated work.
3. Remove changes that lack an accepted requirement and regression test.
4. Preserve physical `AGENTS.md`/`CLAUDE.md`; ensure substantive content is
   mirrored without symlink.

Exit: every changed file has a requirement and test.

### C2 — Resolve CI parity by root cause

1. Reproduce concurrent state-lock exit 127 with inherited stdout/stderr and
   exact executable/PATH evidence.
2. Determine whether the cause is missing executable, environment isolation,
   process limit, resource exhaustion, or test ownership.
3. Fix the owner; do not lower coverage, skip the test, suppress failure, or
   classify it as flaky.
4. Re-run replay, hidden-root, postinstall, runtime matrix, and test-bucket
   selection regressions.
5. Run the complete parity command until every bucket passes.

Exit: targeted tests and full CI parity are green on the same commit.

### C3 — Fork package and runtime delivery

1. Keep upstream npm publication disabled for the fork.
2. Pin Bun and Node at their project owner.
3. Ensure local tools use explicit project executables; no ambient global tool
   or inherited shell startup decides behavior.
4. Build and pack a local artifact named by commit/digest.
5. Install physical artifact contents into the canonical runtime. Do not use
   symlink, link command, path dependency, tag, release, or npm publication.
6. Prove service/proxy behavior after installation and preserve stdio/session
   identity across daemon restart where supported.

Exit: installed artifact digest maps to the merged CCS commit and proxy runtime
passes.

### C4 — Keyring/proxy integration

1. Consume `PROXY_INTERNAL_API_KEY` through approved aliases and
   `env-keyring auto-exec`.
2. Clear inherited names before execution.
3. Validate proxy models endpoint and one real Waza tool-using request.
4. Confirm Claude 402 remains explicit unavailable state and cannot trigger
   fallback.

Exit: proxy success without secret output, inherited credential, or model
substitution.

### C5 — Projection and security

1. Apply generic + detected Bun/JavaScript/TypeScript skills only.
2. Reject FLEXT overlay unless current markers prove CCS uses FLEXT.
3. Prove physical copies and fixed point.
4. Run manifest inventory, npm/Bun audit, Semgrep, Snyk, Gitleaks, Actions
   validation, and native package checks.

Exit: zero omitted manifest/finding and no projection drift.

### C6 — Branches, PR, and landing

1. Classify all 14 branches by protection, reachability, unique work,
   duplication, or uncertainty.
2. Merge current `origin/main` into `crew/agents_audit` with `--no-ff` when
   divergent.
3. Run proxy/runtime first, then the complete validation/security pipeline.
4. Push normally and open a focused PR against `main`.
5. Resolve reviews/checks and merge by merge commit.
6. Validate installed package and proxy from detached `origin/main`.
7. Remove only clean reachable branches/worktrees.

## Required validation

```text
bun run validate
bun run validate:ci-parity
```

Also run project-native package/build checks, Node/Bun runtime matrix, proxy
runtime, physical package install verification, projection fixed point, and the
complete security matrix.

## Exit criteria

- Full CI parity passes without skip or concurrency workaround.
- Physical installed artifact maps to the merged commit.
- Waza proxy runtime passes and quota/auth failures remain red.
- All 14 branches are decisively classified.
- `main` passes post-merge runtime and no increment residue remains.

