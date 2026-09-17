# code-review-graph runtime reference

Same verification basis as the [operations reference](operations.md):
`code-review-graph 2.3.8+dc.3` help output and installed package source.

## Environment variables read by the code

| Variable | Effect (default) | Source |
| --- | --- | --- |
| `CRG_RECURSE_SUBMODULES` | `1`/`true`/`yes` adds `--recurse-submodules` to `git ls-files` in the full build inventory (unset: off). `update` still diffs the root repository with `git diff --name-status <base>`, so member commits report 0 files updated. | `incremental.py` |
| `CRG_DATA_DIR` | Graph data dir when the registry has no entry. | `incremental.py` |
| `CRG_REPO_ROOT` | Overrides repository root detection. | `incremental.py`, `main.py` |
| `CRG_HOME` | Per-user state dir (unset: `~/.code-review-graph`). | `constants.py` |
| `CRG_TOOLS` | MCP tool filter when `--tools` is absent: `all`, `lean`, or CSV (unset: all). | `main.py` |
| `CRG_DETAIL_LEVEL` | Server-wide `minimal`/`standard`/`verbose` override when `--detail` is absent. | `main.py` |
| `CRG_TOOL_TIMEOUT` | Seconds before `detect_changes_tool` returns an error (0: none). | `main.py` |
| `CRG_MAX_CHANGED_FUNCS` | Changed-function cap for change analysis (500). | `changes.py` |
| `CRG_GIT_TIMEOUT` | Git subprocess timeout seconds (30; doctor 10). | `incremental.py`, `changes.py`, `doctor.py` |
| `CRG_PARSE_WORKERS`, `CRG_SERIAL_PARSE`, `CRG_PARSE_EXECUTOR` | Parse parallelism (min(cpu, 8)); `1` forces serial parsing; `process` or `thread` executor. | `incremental.py` |
| `CRG_MAX_WATCH_SCHEDULES` | Directory watch split cap before one recursive watch (24). | `incremental.py` |
| `CRG_VSTORE` | Bundle store root for `build --seed-from` (unset: under `CRG_HOME`). | `vstore.py` |
| `CRG_CHURN_WINDOW_DAYS` | Window for `detect-changes --churn` (90). | `changes.py` |
| `CRG_MAX_IMPACT_DEPTH`, `CRG_MAX_IMPACT_NODES` | Impact traversal bounds (2, 500). | `constants.py` |
| `CRG_ACCEPT_CLOUD_EMBEDDINGS` | `1` suppresses the cloud-egress warning for cloud embedding providers. | `embeddings.py` |

Other `CRG_*` tuning variables exist (daemon restart backoff, BFS limits);
read the source before setting one.

## MCP

- `serve` exposes about 30 tools by default. `--tools lean` keeps
  `get_minimal_context_tool`, `query_graph_tool`, `semantic_search_nodes_tool`,
  `detect_changes_tool`, `get_review_context_tool`, `get_impact_radius_tool`,
  `get_affected_flows_tool` (`main.py` `LEAN_TOOLS`).
- Per-call `repo_root` wins over `serve --repo`, which wins over the server
  cwd; the HTTP transport shares one default root, so pass `repo_root` on
  every call when several checkouts are in use.
- Start with `get_minimal_context_tool(task=...)` and pass
  `detail_level="minimal"`; several tools default to `standard`. A server
  override (`--detail` or `CRG_DETAIL_LEVEL`) replaces every per-call value.
- Read results carry a `_graph` envelope (`built_at_sha`, `built_on_branch`,
  `head_sha`, `head_matches_build`, `updated_at`, `age_seconds`). It compares
  commits only (`tools/_common.py`).
- `build_or_update_graph_tool` and `apply_refactor_tool` are writes.
- AI Hub declares a project-scoped `code-review-graph serve` route in its MCP
  configuration and decides whether it is enabled; a repository-local MCP
  entry written by `install` is not an AI Hub projection.

## Generated skills and hooks written by `install` (`skills.py`)

- Skills: `_SKILLS` renders generic query skills (`explore-codebase`,
  `review-changes`, `debug-issue`, `refactor-safely`; `build-graph` in newer
  fork builds) into each platform's skills dir.
- Claude/Qoder `settings.json`: `PostToolUse` (`Edit|Write`) runs
  `update --skip-flows --repo "$(git rev-parse --show-toplevel)" || true`;
  `SessionStart` runs `status`. Both exit silently without the binary on
  `PATH`. In a submodule the top level is the member root.
- Codex: user-level `~/.codex/hooks.json` with `update --skip-flows` and
  `status` against the cwd.
- Git `pre-commit` (honors `core.hooksPath` and worktrees): `update`, then
  `detect-changes --brief`.
- Gemini hook scripts and most platform MCP entries (`cwd`) embed the absolute
  checkout path at install time, so they are per-checkout files.

## Watchers and daemon

- One watcher per graph. AI Hub supervises watchers through its own service
  (declared in its tools configuration, `ai-hub-watch.service`), which
  `daemon status` does not see: `daemon status` can report "not running" while
  that service is active. Check both before `watch`, `serve --auto-watch`, or
  `daemon start`.
- The daemon reads `watch.toml` under `CRG_HOME`; each `[[repos]]` entry takes
  `path`, `alias`, and optional `data_dir`, `recurse_submodules`, `embedding`,
  exported to its watcher as `CRG_DATA_DIR`, `CRG_RECURSE_SUBMODULES=1`, and
  `CRG_EMBEDDING_MODEL` (`daemon.py`). `daemon add` accepts only the path and
  `--alias`.
- It spawns `code-review-graph watch --repo <path>` per entry and runs one
  initial `build` for an entry without a database.
- A `watch.toml` with a generated header is an AI Hub projection: change the
  workspace policy at its owner; `daemon add|remove` would write into it.
- `daemon status` lists skipped entries whose directory no longer exists;
  `prune` reports them for removal.

## Doctor fixes

| Check | Critical | Fix |
| --- | --- | --- |
| graph | yes | `build --repo <root>` (superproject: with `CRG_RECURSE_SUBMODULES=1`) |
| freshness | no | `update --brief`; `build` when `update` exits 1 |
| mcp-config, serve-cmd | no | AI Hub MCP configuration finding; do not run `install` |
| server (import/boot) | yes | AI Hub installation finding |
| hooks | no | manual `update` after edits; the check reads only `.git/hooks/pre-commit` and Claude/Qoder settings (not `core.hooksPath`, linked worktrees, Gemini, Codex) |
| embeddings | informational | `embed` only when semantic search is required |
