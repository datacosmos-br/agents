# AI Hub runbook

## Repository contract

| Field | Value |
|---|---|
| Remote | `https://github.com/datacosmos-br/ai-hub.git` |
| Integration branch | `dev` |
| Snapshot checkout | `/home/marlonsc/gt/aihub/mayor/rig` treated as an independent Git repo |
| Snapshot state | `dev` ahead by one commit; six tracked files dirty |
| Open PRs | `#563`, `#562`, `#560`, `#558`, `#557`, `#555`, `#554`, `#547`, `#545` |
| Final state | `LANDED_VERIFIED_PENDING_TRACKER` |

No command may use the orchestration implied by the checkout path. Follow
[shared contracts](../01-shared-contracts.md) and
[landing](../03-validation-and-landing.md).

## Mission

Converge AI Hub credential/config owners, generators, project projections,
dependency updates, and open feature branches on `dev`. AI Hub remains the
owner of its generated runtime/MCP/config surfaces; `.agents` must not hand-edit
those outputs.

## Dirty baseline to preserve

Snapshot changes include `.beads/config.yaml`, `.beads/metadata.json`,
`.mise.toml`, `UNIVERSAL_CORE.md`, `skills/beads/worker/SKILL.md`, and `uv.lock`.
The Beads files are outside executable scope: preserve them byte-for-byte and do
not transport them into the work lane unless the operator later reactivates the
tracker.

The ahead commit and remaining dirty hunks must be classified before worktree
creation. No whole-tree copy is allowed.

## Phases

### H1 — Isolate and classify

1. Capture `dev`, local commit, upstream, merge-base, dirty diff, open reviews,
   checks, worktrees, and branch reachability.
2. Create `.worktrees/<work-id>` from `origin/dev`.
3. Cherry-pick the ahead commit only if every change is in scope; otherwise
   apply attributable hunks and record the source SHA.
4. Leave suspended tracker files in the original checkout.

Exit: clean work lane with a documented mapping from every absorbed hunk.

### H2 — Credential and configuration owners

1. Identify the canonical manifest/generator for keyring consumer declarations,
   Mise environment, MCP, services, and project projections.
2. Update owners for the two-secret contract and approved aliases.
3. Regenerate consumers through project commands; never edit generated output.
4. Run generator apply/check twice to prove fixed point.
5. Confirm no `.env`, inherited token, duplicated physical secret, or direct
   secret-file read remains.

Dependency: the Agents keyring contract and CCS runtime must be fixed.

Exit: Bash/Fish/noninteractive runtime and generated config converge.

### H3 — Open PR reconciliation

Process dependency PRs individually after runtime and native gates:

- `#563` rumdl;
- `#562` mypy;
- `#557` pytest;
- `#555` Ruff;
- `#554` Bandit.

For feature/fix PRs `#560`, `#558`, `#547`, and `#545`:

1. Compare the PR tip with current `dev` and local WIP.
2. Identify unique behavior and owner files.
3. Rebuild unique behavior on a clean branch when the original branch mixes
   stale, checkpoint, generated, or conflicting work.
4. Close an original PR only after the substitute commit is on `dev` and its
   SHA is recorded.

Exit: all nine PRs are merged or superseded by reachable integration SHAs.

### H4 — Project projection and security

1. Apply generic + detected Python + FLEXT skills as physical copies.
2. Reject personal workflows and internal development workflow content.
3. Regenerate dependency/Actions policy only through AI Hub owners or the
   accepted upstream generator.
4. Run tracked-manifest security inventory, Python audits, Semgrep, Snyk,
   Gitleaks, Actions checks, and lock fixed point.

Exit: second projection/generation pass produces no diff and every manifest was
scanned.

### H5 — Landing

1. Merge current `origin/dev` into each surviving work branch with `--no-ff`
   when divergent.
2. Run real CLI/config/MCP runtime before native gates.
3. Open focused PRs against `dev`; do not combine dependency PRs or unrelated
   feature replacements.
4. Resolve reviews/checks and merge by merge commit.
5. Validate detached `origin/dev` after each dependency-sensitive merge batch.
6. Remove only clean reachable lanes and obsolete branches.

## Required validation

- Project-native `make help` and canonical runtime/generator commands.
- Full lint, format, type, test, build, security, and generated-config checks.
- Keyring shell/runtime matrix without secret output.
- Project projection fixed point.
- PR/review/check and branch-reachability evidence.

## Exit criteria

- `dev` contains all accepted unique work.
- Nine snapshot PRs are merged or have reachable substitute SHAs.
- No generated drift, credential duplication, omitted security manifest, or
  increment worktree/branch remains.
- Suspended tracker files were not modified by this increment.

