<!-- AIHUB-INVIOLABLE-LAW-PRELUDE v1 -->
# AI Hub Inviolable Law — Strict Prelude

1. Truth: never claim done/green/resolved without command, exit code, decisive output.
2. Root cause: no bypass, fallback, shim, suppression, stub, hardcode, or old+new coexistence.
3. Beads first: claim/update bead before file write, shell, or multi-step work; update after every repo-state change.
4. Research first: inspect code, docs, canonical sources before acting; never invent APIs, flags, facts, or behavior.
5. Owner first: use the project's declared facades/primitives; do not reimplement them locally.
6. Gate discipline: if a gate blocks, stop and escalate with the exact command/edit; never route around it.
7. Landing: native gates, commit, fast-forward push, bead evidence.
8. Divergence: FF push rejected → integrate by cooperation: `git merge --no-ff` the integration base into your lane, resolve conflicts, revalidate, land. Never rebase or force-push a shared branch; never discard another actor's work.
9. Escalation: impossible rule → exact error. Rule conflict → present both with numbers. Unclear → one targeted question. Never guess.
10. Precedence: NEWEST > OLDEST. USER REQUEST > BEADS > ADRs > SKILLs > DOCS > default. Adjust lower/older to higher/newer. Doubt → ASK USER FIRST.
<!-- /AIHUB-INVIOLABLE-LAW-PRELUDE -->

# AGENTS.md — ai-hub

> **Project execution law:** [`AGENTS.md`](https://github.com/datacosmos-br/ai-hub/blob/dev/AGENTS.md).
> Universal engineering core: [`UNIVERSAL_CORE.md`](https://github.com/datacosmos-br/ai-hub/blob/dev/UNIVERSAL_CORE.md). Composition: global skills + project `AGENTS.md` + this project scope. Do not re-embed universal law.
>
> **Standalone / independent mode:** when the canonical remote file does not resolve, pin the raw URL to the same branch or release as this package (never the protected branch).

## Navigation Map

- **Getting started:** `docs/guides/getting-started.md`
- **Architecture:** `docs/guides/architecture.md`
- **Configuration:** `docs/guides/configuration.md`
- **Operations:** `docs/operations.md`
- **Agent guide:** `docs/guides/agent-guide.md`
- **Decision records:** `docs/adr/README.md`
- **Skills index:** `skills/README.md`

<!-- AIHUB-AGENTS-SCOPE-LOCAL-BEGIN -->
<!-- project-specific notes below -->

## Lane lifecycle

Gas Town owns the whole lane lifecycle. This project owns config, services, MCP, CRG, and workspace policy. Work flows through the rig's canonical Gas Town surface:

- `gt sling <bead>` spawns a polecat worktree/branch
- polecat commits, runs `gt done` → merge queue
- Refinery rebases, verifies, merges and closes the bead

```bash
gt sling <bead-id> <rig>
gt hook status
gt done
gt convoy status
```

This project must not create worktrees or branches itself, push, or open pull requests manually; the Refinery owns merges to the default branch. Stop at the integration lane unless the operator explicitly asks to promote.

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
- Never dismiss errors or warnings as pre-existing or cosmetic; always fix at root cause wherever they live before declaring done.
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
- Gas Town owns lane lifecycle; ai-hub owns living runtime registration for beads, serena, CRG, LSP/observer state, and maintenance daemons.
- Rules, managed hooks, and product hook inventory are SSOT under `config/`; foreign agent hooks are warnings like foreign MCPs; managed product hooks stay disabled at the product and route through one socket executor per event type.
- Worktrees created by Gas Town run `make setup` so mise/venv are reconstructed for the lane (`.venv` may be a symlink per the designed layout).
- CI codegen must emit `CI=Y` on generated `ci.yml` / `ci-matrix.yml` / Dockerfiles; under `CI=Y`, `make check` skips executing ruff, pyrefly, and pytest.
- Workspace/worktree watch is incremental and state-driven from last hook or MCP touch (configurable interval and parallelism); first use builds or copies from the parent workspace.
- Rope/LSP activation shares the same observer/MCP/hooks funnel; any git-stored LSP artifacts come from the project generator templates.
- Cursor Shared MCP must resolve the active workspace/worktree across multiple Cursor sessions; its context wiring differs from other agents.
- MCP routing must virtualize session identity so bridges survive daemon restarts without breaking clients.
- In umbrella workspaces, member-repo push does not require fixing workspace gitlinks first; push from the member repo, then roll up gitlinks in the umbrella after those commits are on the remote.
