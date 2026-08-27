# Agents runbook

## Repository contract

| Field | Value |
|---|---|
| Remote | `https://github.com/marlon-costa-dc/agents.git` |
| Integration branch | `dev` |
| Active lane | `fix/exhaustive-pipeline-audit` |
| Active PR | `#4` — `fix: make governance pipelines fail closed` |
| Snapshot state | Branch clean and published; PR `UNSTABLE`; evaluation workflow failing |
| Final state | `LANDED_VERIFIED_PENDING_TRACKER` |

Read [shared contracts](../01-shared-contracts.md) and
[landing procedure](../03-validation-and-landing.md) before changing this
repository.

## Mission

Make `.agents` the portable authority for personal skills, generic project
skills, technology detection, FLEXT-conditioned projection, Waza evaluation,
credential injection, storage governance, MCP checks, and deterministic
security gates.

The current branch contains five commits over the recorded `dev` base and a
382-file diff. It includes valid review fixes and an overbroad mechanical
rewrite of evals. Preserve the former and rebuild the latter.

## Current findings to carry forward

- PR #4 has review findings covering CI triggers, process-group termination,
  token measurement, frozen skills, MCP drift, projection targets, and
  false-green evals.
- CI currently fails because the temp runner expects a machine-local storage
  manifest.
- Default `make check` invokes the suspended Dolt audit.
- `make sync` reports stale personal generic/ECC entries.
- Project projections are not converged.
- 76 skill suites and 228 scenarios were mechanically normalized; examples
  lost task-specific assertions and genuine empty inputs.
- Waza has a typed preflight classifier and model owner, but live validation is
  blocked until the proxy/runtime path is repaired.
- `/tmp`, XDG scratch, and 109 GiB of shared cache require owner-safe cleanup.

## Scope

### In

- Six original PR review fixes and global searches for the same defects.
- Portable `AGENTS_STORAGE_CONFIG` and bounded temp/cache lifecycle.
- Keyring manifest, loader, `env-keyring`, shell bootstrap, and tests.
- Waza model owner, semantic evals, artifact validation, baseline/gate.
- Personal/generic/technology/FLEXT distribution and explicit project roots.
- ECC capability extraction, full ECC/SkillShare removal, short descriptions,
  and `operator-correction-learning` manual mode.
- Deterministic security inventory, MCP drift proof, CI, docs, and PR #4.

### Excluded or dormant

- Operational Gas Town/Beads/Dolt access.
- Changes to the Gas Town repository.
- Distribution of suspended Gas Town/Beads workflows.
- Promotion from `dev` to `main`.

## Phases

### A1 — Reconcile the branch

1. Fetch `origin` and record the current `dev`, branch, PR, review, and check
   SHAs.
2. Compare every changed file with `origin/dev`.
3. Keep the six root-cause review fixes and their tests.
4. Restore semantic content from `origin/dev` where normalization removed real
   assertions, then reapply only required Waza schema/model changes.
5. Remove unrelated archive churn unless its deletion is required by the
   single-authority policy and proven by inventory.

Exit: every changed file maps to a requirement in this runbook.

### A2 — Portable storage and temp governance

1. Add the approved explicit storage-config contract.
2. Remove runtime Dolt execution from default check/CI/status/setup. Preserve
   its code and isolated unit tests.
3. Finish per-run scratch, signal handling, cache variables, reports, limits,
   safe GC, and systemd timer.
4. Validate Bash, Zsh, Fish, Go, Python, Node/Bun, Rust, and Java.
5. Classify and clean only proven orphan storage.

Exit: clean CI runs without user files; temp fixtures and real concurrency pass.

### A3 — Keyring and shells

1. Change the physical proxy owner to `PROXY_INTERNAL_API_KEY`.
2. Declare all approved aliases and clear inherited names before injection.
3. Make alias removal clear only an identically named legacy physical record.
4. Prove login/interactive shells, direct `auto-exec`, Mise, GitHub API, and
   proxy without exposing secrets.

Dependency: representative CCS proxy runtime must already pass.

Exit: two physical records for this domain and no 401.

### A4 — Skills and Waza

1. Repair all 228 scenarios using task-specific fixtures, assertions, and
   negative cases.
2. Set the 240-second behavior limit under the 300-second executor timeout.
3. Run all 76 suites and valid A/B baselines.
4. Extract only useful generic ECC capabilities; remove every other ECC and
   SkillShare identity/sync surface.
5. Make descriptions keyword-only and procedures local references.
6. Validate strict `database-migration` and correction-learning manual mode.
7. Run Waza config apply twice and prove fixed point.

Exit: no false-green grader, no old identity, and live Waza errors remain red.

### A5 — Projections and security

1. Replace implicit town-root discovery with explicit repeatable roots.
2. Apply personal projections and prove generic/technology skills are absent
   from personal homes.
3. Apply project projections to the six approved repositories, excluding Gas
   Town.
4. Prove physical copies, reflink behavior, technology detection, FLEXT
   conditions, and second-apply fixed point.
5. Replace monolithic Snyk discovery with deterministic tracked-manifest scans.
6. Run Semgrep, Snyk, Gitleaks, native audits, Actions validation, and secret
   output checks.

Exit: projection and security matrices are complete with zero omitted target.

### A6 — PR #4 and integration

1. Merge current `origin/dev` with `--no-ff` if divergent.
2. Run runtime, complete native gates, and all projection/MCP checks.
3. Push normally and update PR #4.
4. Resolve every review thread and required check.
5. Merge by merge commit into `dev`.
6. Validate a detached post-merge worktree at `origin/dev`.

Exit: PR #4 merged, `dev` runtime/gates green, lane removed, ledger updated.

## Required gates

Run `make help` first. The final set includes:

```text
make ci
make security
make sync
make sync SCOPE=projects <explicit roots>
make mcp
make temp STATUS=Y
make validate-live
```

The exact project-root syntax must match the approved `agentsctl --root`
interface. No target may silently check zero projects. Do not run `make dolt`.

## Session handoff

Record current SHAs, changed files, runtime, gates, PR/check URLs, unresolved
threads, storage before/after, and next exact command. A new session must not
trust an earlier green result against a different commit.
