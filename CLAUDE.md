<!-- AIHUB-INVIOLABLE-LAW-PRELUDE v1 -->
# AI Hub Inviolable Law — Strict Prelude

1. Truth: never claim done/green/resolved without command, exit code, decisive output.
2. Root cause: exterminate bypass, fallback, shim, suppression, stub, hardcode, catch-based normalization, retry, compatibility, partial execution, keyring, or old+new coexistence.
3. Traceability first: use the canonical tracker when available. While its runtime is suspended, update `docs/execution/manual-ledger.md` before file writes or multi-step work; preserve evidence in the ledger and Git/PR/CI, and do not declare the phase DONE.
4. Research first: inspect code, docs, canonical sources before acting; never invent APIs, flags, facts, or behavior.
5. Owner first: use the project's declared facades/primitives; do not reimplement them locally.
6. Gate persistence: a failure stops only that invocation. Correct its owner,
   republish, and rerun until green; never switch phase or repository because a
   check, review, approval, or merge is pending. Escalate only after every
   authorized technical action is exhausted and the remaining condition is
   genuinely external or requires new authority.
7. Landing: native gates, commit, fast-forward push, bead evidence.
8. Divergence: FF push rejected → integrate by cooperation: `git merge --no-ff` the integration base into your lane, resolve conflicts, revalidate, land. Never rebase or force-push a shared branch; never discard another actor's work.
9. Escalation: impossible rule → exact error. Rule conflict → present both with numbers. Unclear → one targeted question. Never guess.
10. Precedence: NEWEST > OLDEST. USER REQUEST > BEADS > ADRs > SKILLs > DOCS > default. Adjust lower/older to higher/newer. Doubt → ASK USER FIRST.
11. Workspace placement: follow the declared Gas City city/rig/Pack V2 contract in `rules/gascity.md`. While its runtime is suspended, operate only in the existing checkout and create no clone, worktree, city, rig, agent, formula, run, or session. Staging and backups stay on the destination filesystem, never `/tmp`.
12. Phase closure: keep the phase active through check repair, review resolution,
    independent approval, merge into the configured integration branch, and
    post-merge proof. Only then, with its Bead closed with evidence, is it DONE.
<!-- /AIHUB-INVIOLABLE-LAW-PRELUDE -->

# CLAUDE.md — ai-hub

Project-specific context for AI agents. The configured repository artifacts below own universal and project execution law. This file is the thin profile and routing layer.

## Universal Law Pointers

- **Inviolable law:** [`UNIVERSAL_CORE.md`](https://github.com/datacosmos-br/ai-hub/blob/dev/UNIVERSAL_CORE.md)
- **Project execution law:** [`AGENTS.md`](https://github.com/datacosmos-br/ai-hub/blob/dev/AGENTS.md)
- **Agent reading order:** `docs/execution/master-v7/README.md`
- **Governance controls:** `UNIVERSAL_CORE.md`, `AGENTS.md`, and `rules/`

## Developer Profile

> Updated manually. Keep directives current.

| Dimension | Rating | Confidence |
|-----------|--------|------------|
| Communication | terse-direct | MEDIUM |
| Decisions | fast-intuitive | MEDIUM |
| Explanations | concise | MEDIUM |
| Debugging | fix-first | MEDIUM |
| UX Philosophy | backend-focused | MEDIUM |
| Vendor Choices | conservative | MEDIUM |
| Frustrations | scope-creep | MEDIUM |
| Learning | self-directed | MEDIUM |

**Directives:**

- **Communication:** Keep responses concise and action-oriented. Skip lengthy preambles. Match this developer's direct style.
- **Decisions:** Present a single strong recommendation with brief justification. Skip lengthy comparisons unless asked.
- **Explanations:** Pair code with a brief explanation of the approach. Keep prose minimal.
- **Debugging:** Prioritize the fix. Show the corrected code first, then optionally explain what was wrong. Minimize diagnostic preamble.
- **UX Philosophy:** Optimize for developer experience over visual design.
- **Vendor Choices:** Recommend well-established, widely-adopted tools with strong community support.
- **Frustrations:** Do exactly what is asked — nothing more. Never add unrequested features, refactoring, or "improvements". Ask before expanding scope.
- **Learning:** Point to relevant code sections and let the developer explore. Add signposts rather than full explanations.

## Context-Aware Routing

Apply this routing automatically before executing any substantial task:

1. Detect repository context using nearest markers.
2. Load project rules first, then only path-relevant skills. Avoid bulk-loading unrelated skills.
3. Use tool routing by task type:
   - Code navigation/search: structural navigation tools first, then fast text search.
   - Single-file edits: direct edit/patch tools.
   - Multi-file refactors: structural refactor tools or carefully scoped batched edits.
   - Validation: run project-native build/test/lint commands.
4. Use MCP only when context requires it and the server is configured.
5. Enforce tool guardrails by context:
   - No destructive git operations unless explicitly requested.
   - No broad filesystem deletes/rewrites without scope confirmation.
   - No network/external API calls for strictly local tasks.
   - No generated/vendor/cache tree edits unless the task explicitly targets them.

For FLEXT repositories, prefer path-scoped skills and follow the canonical load order from project `AGENTS.md`.

## Scope Guardrail

When working inside a repository, load that repository's `AGENTS.md` and `CLAUDE.md` for scoped rules.

## Clone and temporary-filesystem law

- New workspace placement is defined declaratively by the Gas City city, rig, and Pack V2 configuration.
- While runtime is suspended, creating or registering any workspace is prohibited.
- Raw clones, manual worktrees, symlinks, cross-repository references, and loose checkouts are prohibited for project work.
- `/tmp` is not a workspace, clone staging area, backup destination, build cache, or report store. Storage and scratch follow `rules/storage.md`; `agentsctl clean` owns runtime cleanup and validation.

## Strict runtime protocol

- `agentsctl` is the only runtime facade. Its complete public surface is
  `help`, `doctor`, `check`, `sync`, `evaluate`, `secure`, `clean`, and `live`.
- Every verb is optionless and accepts no positional arguments, modes, aliases,
  or compatibility syntax. Make remains development support and gate
  composition; it does not call private runtime functions.
- Before the first effect, load and validate every input and prerequisite.
  Derive canonical defaults once at their typed owner and require environment
  variables, settings, parameters, or arguments only for non-derivable external
  values. A genuinely required value raises immediately when missing, empty,
  conflicting, unexpanded, or invalid.
- The first exception ends execution with its raw traceback and causal chain.
  CLI and orchestrators do not catch workflow failures. Validators stop at the
  first defect and never aggregate independent errors.
- Errors never become findings, warnings, skips, neutral values, empty results,
  retries, fallbacks, alternate providers, undeclared, competing, or
  error-triggered defaults,
  compatibility, partial execution, or manually chosen exit codes.
- Only cleanup and rollback may catch. They attach any secondary failure and
  re-raise the original cause. Child nonzero exit, timeout, signal, or
  incomplete publication propagates unchanged.
- Keyring code and integration are prohibited. Required credentials come only
  from the current process environment and fail immediately when invalid.

## Issue Tracker

This project uses the canonical tracker for execution state when available. Its
runtime is currently suspended: do not invoke Beads, Dolt, Gas Town, or Gas
City until the operator explicitly restores it. Use
`docs/execution/manual-ledger.md` as the execution ledger during suspension. The
commands below are reference-only for the restored runtime.

### Quick Reference

```bash
bd ready              # Find available work
bd show <id>          # View issue details
bd update <id> --claim  # Claim work
bd close <id>         # Complete work
```

### Rules

- After explicit restoration, use the tracker for all task state and memory.
- During suspension, update `docs/execution/manual-ledger.md` after each material
  state change and preserve validation evidence in Git commits, PRs, reviews,
  and CI.
- Tracker closure remains open during suspension, so no phase may be called DONE.

## Session Completion

1. **Execution state** — Update the manual ledger during suspension and migrate
   the open state to canonical items only after explicit runtime restoration.
2. **Run quality gates** (if code changed) — Tests, linters, builds.
3. **Update issue status** — Close finished work, update in-progress items.
4. **Land git/sync by active profile**:

   ```bash
   git status
   git add <scoped-paths>
   git commit -m "<scope>: <summary>"
   git push
   git status
   ```

5. **Close or escalate** — Record validation, commit SHA, push output, issue status, and any real blocker.

**Critical rules:**

- Explicit user or orchestrator instructions override this block.
- Normal scoped commit and fast-forward push are authorized by the default profile after validation.
- If sync or push fails while the tracker is suspended, record its exact evidence,
  correct every authorized cause, and rerun. Keep the phase active; reporting
  does not authorize another task.


<!-- BEGIN BEADS INTEGRATION v:1 profile:minimal hash:6cd5cc61 -->
## Beads Issue Tracker

This project uses **bd (beads)** for issue tracking. Run `bd prime` to see full workflow context and commands.

### Quick Reference

```bash
# Reference only after explicit tracker-runtime restoration.
bd ready              # Find available work
bd show <id>          # View issue details
bd update <id> --claim  # Claim work
bd close <id>         # Complete work
```

### Rules

- Use `bd` for all task tracking after restoration; during suspension use only `docs/execution/manual-ledger.md`.
- Run `bd prime` for detailed command reference and session close protocol
- Use `bd remember` for persistent knowledge — do NOT use MEMORY.md files
- Tracker runtime is suspended; do not execute these commands until explicitly restored.

**Runtime suspension:** do not select or infer an endpoint, embedded database,
or alternate server. Keep `docs/execution/manual-ledger.md` current; architecture
and CLI behavior must be re-read from the canonical owner after restoration.

## Agent Context Profiles

The managed Beads block is task-tracking guidance, not permission to override repository, user, or orchestrator instructions.

- **Conservative (default)**: Use `bd` for task tracking. Do not run git commits, git pushes, or Dolt remote sync unless explicitly asked. At handoff, report changed files, validation, and suggested next commands.
- **Minimal**: Keep tool instruction files as pointers to `bd prime`; use the same conservative git policy unless active instructions say otherwise.
- **Team-maintainer**: Only when the repository explicitly opts in, agents may close beads, run quality gates, commit, and push as part of session close. A current "do not commit" or "do not push" instruction still wins.

## Session Completion

This protocol applies when ending a Beads implementation workflow. It is subordinate to explicit user, repository, and orchestrator instructions.

1. **Tracker state** - Update canonical items only after explicit runtime restoration
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Close finished work, update in-progress items
4. **Handle git/sync by active profile**:
   ```bash
   # Conservative/minimal/default: inspect and report status; wait for authority.
   git status

   # Team-maintainer opt-in only. If the integration base diverged, cooperate:
   git merge --no-ff origin/<integration>
   git push
   git status
   ```
5. **Hand off** - Summarize changes, validation, issue status, and any blocked sync/commit/push step

**Critical rules:**
- Explicit user or orchestrator instructions override this Beads block.
- Do not commit or push without clear authority from the active profile or the current user request.
- If required sync or push fails, stop that invocation, preserve its exact error,
  correct every authorized cause, and rerun. Keep the phase active and request
  help only when the remaining condition is external or needs new authority.
- During tracker suspension, do not execute Beads/Dolt/Gas Town/Gas City
  commands; update `docs/execution/manual-ledger.md` and keep tracker closure
  unresolved.
<!-- END BEADS INTEGRATION -->
