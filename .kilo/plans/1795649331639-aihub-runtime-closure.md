# Plan: finish the ai-hub runtime closure (agents plan is DONE)

Supersedes `.kilo/plans/1795618996552-agents-governance-final.md`; that plan's agents
scope is complete and its file should be deleted by the implementer (history is in Git).

## Status measured 2026-11-26T00:1xZ

### agents (DONE — do not redo)
- PRs #444/#445 merged; `dev` = `b8c1d6ea`.
- 14 delivered/superseded `docs/plans/*` records deleted; only `20260921` (in progress,
  `ag-t8r3`), `20261125` (DONE agents scope) and `pydantic-governance-plan` (ACTIVE) remain.
- `clean-architecture` + `dep-injection` → `skills/project-wide/architecture/`;
  `runtime-level` → `skills/technology/`; ADR-0002 amended.
- `make audit` 128 skills; `make docs` green; one `## The delivery cycle`.
- `ag-b3hm` commented: mise 2026.11.14 handles `lockfile_version = 4`; no warning reproduces.
- `gc mail` broadcast sent.

### ai-hub (IN PROGRESS — this plan)
- Lane `runtime/adopt-and-worktree-scope-20261125`, HEAD `715e6c79f` =
  `merge --no-ff origin/dev (deb20153e)`, which carries the merged gateway fix #1874.
- `make upg` done: agents-governance lock now `b8c1d6ea`; `uv.lock` matches HEAD (no diff).
- `make setup` done.
- `make check CHECK_PHASE=primary` was green (lint 0, pyrefly 0) before the latest
  concurrent rewrite; it must be re-run.
- **A concurrent actor is actively rewriting the config overlay** in this same checkout.
  Current worktree (staged): `src/ai_hub/_config.py`, `docs/guides/configuration.md`,
  `tests/unit/test_aihub_config_env_seam.py`. Its new
  `_AiHubConfigOverlaySource` merges a same-name overlay over the package base with
  `concatenate_lists=False` — the correct DRY contract (lists replace, no duplicate
  entries). Adopt it; never revert it (law 11).
- **The live runtime defect is unfixed and was reverted**: `gateway_builder.py:216-224`
  still raises `PermissionError("... no route usable outside a Git repository ...")`
  for a project-less session whose every authorized route is checkout-scoped. That
  kills `tools/list` and is the `mcp connected` failure in
  `journalctl --user -u ai-hub-mcp.service` for agent `claude`.
- **Worktrees**: `mcp_authorize_project_root(<worktree>)` fails with "not an active
  governed workspace" when the worktree is absent from `workspaces.json`. Canonical
  contract: a linked worktree is governed only when Git maps it to a configured
  principal (`docs/worktrees.md`, Resolution rules 4 and 7) and it must be activated
  (`tests/unit/test_aihub_current_governed_checkout.py:31`). Activation is performed by
  `mcp_observe_project_root` on a project-bearing request
  (`services/_mcp/gateway_catalog.py:66-68`). Do not bypass the activation check.
- `make deploy` refuses until `uv.lock`/locks are committed (observed:
  "checkout deployment requires committed locks: M uv.lock").
- Operator decision already recorded in `src/ai_hub/config/services.yaml`: runtime
  source is `checkout`. The stable-console freeze was explicitly rejected
  ("eu nunca pedi, isso"). Keep `runtime.source: checkout`.

## Authorities (read before edits)
- `AGENTS.md` + `rules/law.md` (13 outcomes; law 1 truth, 8 fail loud on one path,
  9 repair production not the test, 10 Done, 11 never destroy another's work).
- `src/ai_hub/config/services.yaml` — `runtime.source: checkout` (deploy from the
  integration checkout, not a frozen console).
- `docs/worktrees.md` — identity axes; Resolution rules 1-7; worktrees share project
  and ledger identity and keep their own checkout path.
- `docs/adr/0016-parameterized-gitflow-lanes-and-worktree-lifecycle.md` — lane owner.
- `src/ai_hub/services/_mcp/gateway_builder.py:188` — `catalog_tools`.
- `src/ai_hub/services/_mcp/gateway_catalog.py:66` — observe-before-authorize.
- `src/ai_hub/_utilities/mcp_workspace.py:74` — `mcp_resolve_project_root`;
  `:86` area — `mcp_authorize_project_root` (activation check).
- `tests/unit/test_aihub_current_governed_checkout.py:31` — activation is mandatory.
- `config/codegen.yaml` — generated projections; never hand-edit `_models/_config/*`
  or `_protocols/_config/*`; regenerate and require a 2x no-op diff.

## Ordered tasks

### 0. Coordination freeze (do this first)
- Identify the concurrent actor editing `src/ai_hub/_config.py`: `git worktree list`,
  `bd list --status in_progress`, `gc mail inbox` / gc threads. It is writing the
  config overlay in the primary checkout.
- Announce the claim on the inter-session channel (bead + `gc mail`) and wait until
  `git status`/`git diff` for `_config.py`, `docs/guides/configuration.md` and
  `tests/unit/test_aihub_config_env_seam.py` is stable across two reads (no change
  between consecutive `git diff --stat`). Never edit those files while the actor is live.
- If the actor cannot be identified, stop and report; do not race it.

### 1. Adopt and prove the config overlay (operator directive: overrides, no duplicates)
- Read the final `_AiHubConfigOverlaySource` and confirm same-name overlay uses
  `merge_values(..., concatenate_lists=False)`; lists replace, different base files
  still concatenate.
- Run `pytest tests/unit/test_aihub_config_env_seam.py -q` → all pass, including
  `test_partial_override_preserves_every_governed_domain`.
- Run `make setup` (mandatory), then `make check CHECK_PHASE=primary`; loop
  setup→check until green. `make check` full is refused above load 20; primary is the
  sanctioned gate.
- Commit the adopted overlay as its own commit with attribution; it is the concurrent
  actor's work, adopted not rewritten.

### 2. Fix the project-less `tools/list` (the `mcp connected` defect)
- In `catalog_tools` (`gateway_builder.py:188-224`), when
  `mcp_session_has_project()` is false and the filtered route tuple is empty, `return ()`
  instead of raising. Keep the per-route `NoProjectError` on invocation: the listing is
  healthy and empty; the call is the one failing path (law 8).
- Add a unit test covering "no project + only checkout-scoped routes → empty tuple, no
  exception"; place it with the existing gateway/MCP tests.
- Do not add `# noqa`, `type: ignore`, `cast`, `Any`, or `extra="ignore"`.

### 3. Prove worktree permission inheritance without bypassing activation
- Verify a worktree session lists project tools after the observe step:
  request with header = worktree git root → `mcp_observe_project_root` records it →
  `mcp_authorize_project_root` returns the worktree path.
- If authorization still fails, fix the *observation* path (ensure the bridge sends the
  worktree root and the catalog middleware observes it before `tools/list`), never by
  removing the activation requirement in `current_governed_checkout`
  (`test_aihub_current_governed_checkout.py:31`).
- Add a regression test for a linked worktree: unauthorized first request is refused,
  observed request authorizes, subsequent `tools/list` exposes that worktree's routes.

### 4. Validate the runtime from the checkout (before deploy)
- `make setup` → `make check CHECK_PHASE=primary` → loop.
- Exercise the gateway from this checkout with a home-cwd session (expect empty catalog,
  no error) and a worktree session (expect project tools).
- Inspect `journalctl --user -u ai-hub-mcp.service --no-pager` for the absence of
  `no route usable outside a Git repository` and for `POST /mcp ... 200`.

### 5. Deploy and prove the live service
- Commit everything including `uv.lock` (deploy refuses uncommitted locks).
- `make upg` if the overlay/dep work changed locks; commit the lock.
- `make deploy` (checkout source). Then:
  - `systemctl --user is-active ai-hub-mcp.service` = active.
  - `systemctl --user status ai-hub-mcp.service` shows `ExecStart` and WorkingDirectory
    from `/home/marlonsc/ai-hub/.venv` (one stable console, one checkout).
  - `journalctl --user -u ai-hub-mcp.service` shows no `PermissionError`; `tools/list`
    returns 200.
  - `make mcp` doctor passes.
  - `~/.local/bin/ai-hub` still resolves to `/home/marlonsc/ai-hub/.venv/bin/ai-hub`.
- Confirm no lane session deployed its own venv over the console (the "three versions"
  symptom): only the integration checkout deploys.

### 6. Full tests
- `make tests` (incremental Testmon). If a gate is refused by host load, use the
  sanctioned lighter form for that verb; do not add an admission override unless the
  operator authorizes it.
- Fix failures at the source/template, never in generated projections. Regenerate and
  require a 2x no-op diff for any generated file.

### 7. Land (only after DONE above)
- `git fetch origin`, `git merge --no-ff origin/dev` into the lane, resolve by adopting
  the integration tip, re-run `make setup` → `make check CHECK_PHASE=primary` → `make tests`.
- Commit, push, open a PR to `dev`. Required greens: `Runtime-first governance validation`,
  CodeQL, `Analyze` ×5, semgrep. `cubic`/`Kilo Code Review` may stay pending; merge on
  the required set.
- Merge with `--no-ff`, confirm with `gh pr view <n> --json state,mergedAt,mergeCommit`,
  then `git merge --no-ff origin/dev` into the checkout, `make setup`, `make check
  CHECK_PHASE=primary`, `make deploy`, and re-prove the logs.
- Broadcast the landing via `gc mail send --city /home/marlonsc/gc --all ...` (no `--from`).

### 8. Cleanup (Phase V)
- Delete the superseded agents plan file `.kilo/plans/1795618996552-agents-governance-final.md`.
- Retire the local duplicate ai-hub MCP history (`1f0c28322`, `88042159e`) that the
  merged #1874 supersedes: keep the branch reachable until the PR merges, then let
  `ai-hub wip sweep --apply` retire it with ancestry proof; never force-delete.
- Prune stale `workspace-activation` residue (the pytest `tmp` entries and dead worktree
  paths) only through the owning reconcile/activation mechanism, not by hand-editing
  `~/.local/state/ai-hub/workspaces*.json`.

## Validation checklist (evidence required per step)
- `git -C /home/marlonsc/ai-hub status -sb` clean at the lane tip.
- `make setup` exit 0; `make check CHECK_PHASE=primary` exit 0 (lint 0, pyrefly 0).
- `pytest tests/unit/test_aihub_config_env_seam.py` 5 passed.
- New gateway test: project-less session → `()`; invocation → `NoProjectError`.
- Worktree test: observe-before-authorize path returns the worktree root.
- `make tests` exit 0.
- `make deploy` exit 0; unit active; logs show `tools/list` 200 and no `PermissionError`.
- `make mcp` exit 0; `~/.local/bin/ai-hub` → the single checkout venv.
- PR merged; `dev` updated; post-merge setup/check/deploy green.

## Risks / guards
- **Active concurrent writer** on `_config.py`, docs, tests: adopt, never revert; pause
  until stable. Re-checking is mandatory because it reverted the gateway fix once.
- **No masking**: forbid `# noqa`, `# type: ignore`, `cast`, `Any`, `extra="ignore"`.
- **Generated is projection**: never edit `_models/_config/*` or `_protocols/_config/*`;
  fix `config/codegen.yaml`/templates and require a 2x no-op diff.
- **Do not freeze the console**: `runtime.source` stays `checkout`; the operator rejected
  the stable-console option.
- **Do not bypass worktree activation**: the canonical contract requires activation;
  fix observation, not the check.
- **Do not hand-run the full `make check`** under load > 20; use `CHECK_PHASE=primary`.
- **Do not deploy with dirty locks**; commit `uv.lock` from `make upg` first.
- **No merge before DONE**; defer PR merge until setup/check/tests/runtime proof are all
  green on the lane tip.

## Out of scope
- Re-freezing the client/service in `~/.local/bin/ai-hub` (operator rejected it).
- FLEXT workspace/Makefile regeneration and FLEXT template headers (other owners).
- Any change to the already-merged agents plan scope.
