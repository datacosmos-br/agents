<!-- AIHUB-INVIOLABLE-LAW-PRELUDE v1 -->
# AI Hub Inviolable Law — Strict Prelude

1. Truth: never claim done/green/resolved without command, exit code, decisive output.
2. Root cause: exterminate bypass, fallback, shim, suppression, stub, hardcode, catch-based normalization, retry, compatibility, partial execution, keyring, or old+new coexistence.
3. Tracker first: use the canonical tracker only when selected and available. If its runtime is explicitly suspended, create no substitute tracker or ledger; preserve evidence in separately authorized Git/PR/CI and do not declare the phase DONE.
4. Research first: inspect code, docs, canonical sources before acting; never invent APIs, flags, facts, or behavior.
5. Owner first: use the project's declared facades/primitives; do not reimplement them locally.
6. Gate persistence: a failure stops only that invocation. Correct its owner,
   republish, and rerun until green; never switch phase or repository because a
   check, review, approval, or merge is pending. Escalate only after every
   authorized technical action is exhausted and the remaining condition is
   genuinely external or requires new authority.
7. Landing: native gates, commit, fast-forward push, bead evidence.
8. Divergence: FF push rejected → integrate by cooperation: `git merge --no-ff` the integration base into your lane, resolve conflicts, revalidate, land. Never rebase or force-push an authorized change or integration branch; adopt all current worktree state and fix it forward.
9. Escalation: impossible rule → exact error. Rule conflict → present both with numbers. Unclear → one targeted question. Never guess.
10. Precedence: NEWEST > OLDEST. USER REQUEST > BEADS > ADRs > SKILLs > DOCS > default. Adjust lower/older to higher/newer. Doubt → ASK USER FIRST.
11. Workspace placement: follow the declared Gas City city/rig/Pack V2 contract in `rules/coordination/gascity.md`. While its runtime is suspended, operate only in the existing checkout and create no clone, worktree, city, rig, agent, formula, run, or session. Staging and backups stay on the destination filesystem, never `/tmp`.
12. Phase closure: keep the phase active through check repair, review resolution,
    independent approval, merge into the configured integration branch, and
    post-merge proof. Only then, with its Bead closed with evidence, is it DONE.
    When the operator states that no independent reviewer exists and authorizes
    an administrative merge, that authorization replaces the approval row alone;
    every other row stays mandatory and closure records the approval as
    operator-authorized, never as satisfied.
<!-- /AIHUB-INVIOLABLE-LAW-PRELUDE -->

# AGENTS.md — ai-hub

> **Project execution law:** [`AGENTS.md`](https://github.com/datacosmos-br/ai-hub/blob/dev/AGENTS.md).
> Composed governance: `config/governance.json` selects canonical `rules/`,
> `skills/`, `commands/`, and this project scope. `agentsctl sync` projects the
> composition through provider-native instructions and lifecycle hooks. Do not
> re-embed canonical rule or skill procedures here.
>
> **Standalone / independent mode:** when the canonical remote file does not resolve, pin the raw URL to the same branch or release as this package (never the protected branch).

## Navigation Map

- **Repository overview:** `README.md`
- **Active execution package:** `docs/execution/master-v7/README.md`
- **Decision records:** `docs/adr/README.md`
- **Security evidence:** `docs/security/security-triage.md`
- **Skills index:** `skills/README.md`

<!-- AIHUB-AGENTS-SCOPE-LOCAL-BEGIN -->
<!-- project-specific notes below -->

## Change lifecycle

Gas City configuration owns orchestration identity and dispatch; the repository owns Git, native gates, PR review, and landing. The canonical contract is `rules/coordination/gascity.md`, which owns how a city's activation state is resolved: read it from that city's own authority at preflight and invoke no orchestration command outside the scope that authority has explicitly activated. Work in the existing checkout and stop at the configured integration branch unless the operator explicitly asks to promote.

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

The composed governance owners define closure. Local delta only:

- Integration lane is where an increment must be running to count as closed.
- The closure surface must leave no lane worktree, no open PR, and no open tracker item for the increment.
- Zero residue at increment end: dead code, compat shims, un-rewired consumers/tests are defects, never carry-over.
<!-- AIHUB-AGENTS-SCOPE-LOCAL-END -->

## Learned User Preferences

- Stop landing at `dev`; promote to `main` only when the operator explicitly asks.
- Finish PRs, tracker items, worktrees, branches, and CI/lint/test failures through the integration lane.
- During multi-lane work, continuously fast-forward absorb `origin/dev` so landed features stay integrated.
- Never dismiss any violation as pre-existing or cosmetic; always fix it at its root cause before declaring done. Production ships only complete versions: `rules/workflow/production-readiness.md` owns adopting every defect in the blast radius, including pre-existing ones.
- Leave no optional work behind: absorb, correct, and validate through the canonical execution path before closing a tracker item.
- Fix generated config at config/SSOT or overlays, never by hand-editing generated projections.
- Regenerate generated config via the project generator; doctor/inspect/compare generated config before restarting and watching logs.
- MCP/stdio bridges must not hang indefinitely; daemon restarts must keep the stdio bridge usable (virtualize/preserve session identity across restarts).
- After MCP or daemon deploy changes, validate in-process (for example via opencode) then ask the operator to restart the Cursor MCP client before claiming Cursor-side green.
- Unit/integration and propagate gates must not require auth API keys or live LLM model calls; model-dependent coverage stays minimal.
- Validation workflows that require unavailable external tokens are excluded
  before invocation and recorded as `NOT EXECUTED`, never green; their absence
  does not block offline gates, landing, or post-merge proof. If invoked, they
  retain strict fail-loud credential and runtime semantics.
- Prefer config-key-only documentation (reference config keys, not hardcoded default paths).
- Prefer owner-first reuse and simplification over local reimplementation; structure large work as epic plus sub-epics with separate enforcement/validation tracker items and incremental deliveries.
- Plans and multi-phase work must align docs, tracker, worktrees/branches/PRs with runtime reality before later phases.
- Close a bead only after proving the feature on canonical execution paths in all supported forms.

## Learned Workspace Facts

- This checkout keeps its Beads identity and `agents` database in local
  `.beads/metadata.json`, while `.envrc` inherits the single managed Dolt
  endpoint published by Gas City in
  `$HOME/gc/.gc/runtime/packs/dolt/dolt-state.json`. Do not set `BEADS_DIR` to
  `$HOME/gc/.beads` for this project: that selects Gas City's root identity and
  `hq`, not this project's `agents` ledger. Preflight `bd context --json`,
  `bd ping --json`, and a stdin dry run before imports.
- ai-hub Beads/Dolt is the shared user database on the primary checkout (`config.AiHub.paths.ai_hub`), not a per-worktree private DB.
- Related multi-repo set for shared doc/policy work is declared in configuration.
- Gas City configuration owns orchestration identity; ai-hub owns living runtime registration for tools, CRG, LSP/observer state, and maintenance daemons.
- Rules and MCP inventory are SSOT under `config/`; an unattributable foreign
  agent runtime is a blocking ownership violation. Agent-domain behavior runs
  only through optionless `agentsctl` verbs. Repository Git hooks are extinct;
  provider-native lifecycle hooks are generated artifacts owned by `sync`.
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
