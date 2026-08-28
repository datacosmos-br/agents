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

# AGENTS.md — ai-hub

> **Project execution law:** [`AGENTS.md`](https://github.com/datacosmos-br/ai-hub/blob/dev/AGENTS.md).
> Universal engineering core: [`UNIVERSAL_CORE.md`](https://github.com/datacosmos-br/ai-hub/blob/dev/UNIVERSAL_CORE.md). Composition: global skills + project `AGENTS.md` + this project scope. Do not re-embed universal law.
>
> **Standalone / independent mode:** when the canonical remote file does not resolve, pin the raw URL to the same branch or release as this package (never the protected branch).

## Navigation Map

- **Repository overview:** `README.md`
- **Active execution package:** `docs/execution/master-v7/README.md`
- **Manual execution ledger:** `docs/execution/manual-ledger.md`
- **Decision records:** `docs/adr/README.md`
- **Security evidence:** `docs/security/security-triage.md`
- **Skills index:** `skills/README.md`

<!-- AIHUB-AGENTS-SCOPE-LOCAL-BEGIN -->
<!-- project-specific notes below -->

## Change lifecycle

Gas City configuration owns orchestration identity and dispatch; the repository owns Git, native gates, PR review, and landing. The canonical static contract is `rules/gascity.md`. Gas City runtime is currently suspended, so no orchestration command may be invoked or inferred. Work in the existing checkout and stop at the configured integration branch unless the operator explicitly asks to promote.

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

## Sprint closure

Universal law owns closure. Local delta only:

- Integration lane is where an increment must be running to count as closed.
- The closure surface must leave no lane worktree, no open PR, and no open tracker item for the increment.
- Zero residue at increment end: dead code, compat shims, un-rewired consumers/tests are defects, never carry-over.
<!-- AIHUB-AGENTS-SCOPE-LOCAL-END -->

## Learned User Preferences

- Stop landing at `dev`; promote to `main` only when the operator explicitly asks.
- Finish PRs, tracker items, worktrees, branches, and CI/lint/test failures through the integration lane.
- During multi-lane work, continuously fast-forward absorb `origin/dev` so landed features stay integrated.
- Never dismiss any violation as pre-existing or cosmetic; always fix it at its root cause before declaring done.
- Leave no optional work behind: absorb, correct, and validate through the canonical execution path before closing a tracker item.
- Fix generated config at config/SSOT or overlays, never by hand-editing generated projections.
- Regenerate generated config via the project generator; doctor/inspect/compare generated config before restarting and watching logs.
- MCP/stdio bridges must not hang indefinitely; daemon restarts must keep the stdio bridge usable (virtualize/preserve session identity across restarts).
- After MCP or daemon deploy changes, validate in-process (for example via opencode) then ask the operator to restart the Cursor MCP client before claiming Cursor-side green.
- Unit/integration and propagate gates must not require auth API keys or live LLM model calls; model-dependent coverage stays minimal.
- Prefer config-key-only documentation (reference config keys, not hardcoded default paths).
- Prefer owner-first reuse and simplification over local reimplementation; structure large work as epic plus sub-epics with separate enforcement/validation tracker items and incremental deliveries.
- Plans and multi-phase work must align docs, tracker, worktrees/branches/PRs with runtime reality before later phases.
- Close a bead only after proving the feature on canonical execution paths in all supported forms.

## Learned Workspace Facts

- ai-hub Beads/Dolt is the shared user database on the primary checkout (`config.AiHub.paths.ai_hub`), not a per-worktree private DB.
- Related multi-repo set for shared doc/policy work is declared in configuration.
- Gas City configuration owns orchestration identity; ai-hub owns living runtime registration for tools, CRG, LSP/observer state, and maintenance daemons.
- Rules and MCP inventory are SSOT under `config/`; an unattributable foreign
  agent runtime is a blocking ownership violation. Agent-domain behavior runs
  only through optionless `agentsctl` verbs; repository hooks are extinct.
- Every declared workspace must reconstruct dependencies locally; cross-repository dependency links are prohibited.
- CI runs the complete `make ci` owner. `check`, `static`, and `test` remain
  separate blocking stages; setting `CI=Y` never authorizes omitting them.
- Workspace/worktree watch is incremental and state-driven from the canonical
  observer/MCP owner; first use builds or copies from the parent workspace.
- Rope/LSP activation shares the same observer/MCP funnel; any Git-stored LSP
  artifacts come from project generator templates.
- Cursor Shared MCP must resolve the active workspace/worktree across multiple Cursor sessions; its context wiring differs from other agents.
- MCP routing must virtualize session identity so bridges survive daemon restarts without breaking clients.
- In umbrella workspaces, member-repo push does not require fixing workspace gitlinks first; push from the member repo, then roll up gitlinks in the umbrella after those commits are on the remote.

<!-- BEGIN BEADS INTEGRATION v:1 profile:minimal hash:6cd5cc61 -->
## Beads Issue Tracker

This project uses **bd (beads)** for issue tracking. Run `bd prime` to see full workflow context and commands.

### Quick Reference

```bash
bd ready              # Find available work
bd show <id>          # View issue details (server)
bd where <id>         # canonical locator when tracker runtime is restored
bd update <id> --claim --parent <epic> --assignee "..." --append-notes "..."
bd link <a> <b>       # dependency (default "blocks"; --type parent-child|related)
bd set-state <id> mode:co-tracked   # event + label (co-track Mayor P0 live)
bd close <id> --reason "..."        # only Owner may close
# Runtime commands are suspended by operator instruction.
```

### Rules

- Use `bd` for all task tracking after runtime restoration; during suspension use only `docs/execution/manual-ledger.md`.
- Run `bd prime` for detailed command reference and session close protocol
- Use `bd remember` for persistent knowledge — do NOT use MEMORY.md files
- Tracker runtime is suspended; do not execute these commands until explicitly restored.

**Runtime suspension (P0):** Beads, Dolt, Gas Town, and Gas City are unavailable. Do not select an endpoint, embedded database, or alternate server. Keep `docs/execution/manual-ledger.md` current.

**NEVER:** invent flags, routing, ownership, endpoints, or compatibility behavior. Consult the installed CLI help only after runtime is restored.

## Agent Context Profiles

The managed Beads block is task-tracking guidance, not permission to override repository, user, or orchestrator instructions.

- **Conservative (default)**: Use `bd` for task tracking. Do not run git commits, git pushes, or Dolt remote sync unless explicitly asked. At handoff, report changed files, validation, and suggested next commands.
- **Minimal**: Keep tool instruction files as pointers to `bd prime`; use the same conservative git policy unless active instructions say otherwise.
- **Team-maintainer**: Only when the repository explicitly opts in, agents may close beads, run quality gates, commit, and push as part of session close. A current "do not commit" or "do not push" instruction still wins.

## Session Completion

This protocol applies when ending a Beads implementation workflow. It is subordinate to explicit user, repository, and orchestrator instructions.

1. **Record remaining work** - Update the manual ledger during suspension; create Beads only after restoration
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update execution status** - Update the manual ledger during suspension; update issues after restoration
4. **Handle git/sync by active profile**:
   ```bash
   # Conservative/minimal/default: report status and proposed commands; wait for approval.
   git status

   # Team-maintainer opt-in only, unless current instructions forbid it:
   git fetch origin
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
<!-- END BEADS INTEGRATION -->

<!-- BEGIN BEADS CODEX SETUP: generated by bd setup codex -->
## Beads Issue Tracker

Use Beads (`bd`) for durable task tracking in repositories that include it. Use the `beads` skill at `.agents/skills/beads/SKILL.md` (project install) or `~/.agents/skills/beads/SKILL.md` (global install) for Beads workflow guidance, then use the `bd` CLI for issue operations.

### Quick Reference

```bash
bd ready                # Find available work
bd show <id>            # View issue details
bd update <id> --claim  # Claim work
bd close <id>           # Complete work
bd prime                # Refresh Beads context
```

### Rules

- Use `bd` for all task tracking after restoration; during suspension use only `docs/execution/manual-ledger.md`.
- Run `bd prime` when Beads context is missing or stale. Codex 0.129.0+ can load Beads context automatically through native hooks; use `/hooks` to inspect or toggle them.
- Keep persistent project memory in Beads via `bd remember`; do not create ad hoc memory files.

**Runtime suspension:** do not invoke Beads, Dolt, Gas Town, or Gas City until the operator explicitly restores the canonical runtime. Record execution state in `docs/execution/manual-ledger.md` and preserve evidence in Git commits, PRs, reviews, and CI.
<!-- END BEADS CODEX SETUP -->
