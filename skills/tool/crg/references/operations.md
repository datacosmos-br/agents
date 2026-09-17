# code-review-graph operations reference

<<<<<<< HEAD
Verified against `code-review-graph 2.3.8+dc.3` (the ai-hub `dc-use` fork
=======
Verified against `code-review-graph 2.3.8+dc.3` (the AI Hub `dc-use` fork
>>>>>>> origin/dev
build): each fact below comes from `code-review-graph <sub> --help` or the
installed package source named in parentheses. Re-verify with `--help` after
any version change; the help output wins over this page.

## Command surface

| Need | Command | Notes |
| --- | --- | --- |
| Health checklist | `doctor [--repo R]` | Checks graph, freshness, mcp-config, serve-cmd, server, hooks, embeddings; exit 1 only on a critical failure (`doctor.py`). |
<<<<<<< HEAD
| Stats and provenance | `status [--repo R] [--json] [--data-dir D]` | JSON keys `built_on_branch`, `built_at_commit`, `current_branch`, `current_sha`. Read-only; exits 1 when no graph exists. |
| Full build | `build [--repo R] [--skip-flows] [--skip-postprocess] [--data-dir D] [--seed-from [STORE]] [-q]` | Re-parses every tracked file. |
| Incremental update | `update [--base B] [--repo R] [--brief] [--skip-flows] [--skip-postprocess] [--data-dir D] [-q]` | Default base is the stored built commit. Exits 1 with no graph or no usable base (`tools/build.py`). `--brief` also prints the risk summary. |
| Post-processing only | `postprocess [--repo R] [--no-flows] [--no-communities] [--no-fts] [--data-dir D]` | Re-runs flows, communities, and FTS on an existing graph. |
=======
| Stats and provenance | `status [--repo R] [--json] [--data-dir D]` | JSON keys `built_on_branch`, `built_at_commit`, `current_branch`, `current_sha`. Plain output warns on a branch mismatch only. Exits 1 when no graph exists (`cli.py`). |
| Full build | `build [--repo R] [--skip-flows] [--skip-postprocess] [--data-dir D] [--seed-from [STORE]] [-q]` | Re-parses every tracked file. |
| Incremental update | `update [--base B] [--repo R] [--brief] [--skip-flows] [--skip-postprocess] [--data-dir D] [-q]` | Default base is the stored built commit. Exits 1 with no graph or no usable base (`tools/build.py`). `--brief` also prints the risk summary. |
| Post-processing only | `postprocess [--repo R] [--no-flows] [--no-communities] [--no-fts] [--data-dir D]` | Recomputes signatures, FTS, flows, and communities on an existing graph (`postprocessing.py`). |
>>>>>>> origin/dev
| Embeddings | `embed [--repo R] [--provider local\|openai\|google\|minimax\|voyage] [--model M] [--data-dir D]` | `local` needs the `embeddings` extra; without embeddings search uses FTS5. |
| Change analysis | `detect-changes [--base B] [--brief] [--repo R] [--churn]` | Read-only; default base `HEAD~1`; never re-parses. |
| Impact | `impact [--files F...] [--depth N] [--max-results N] [--base B] [--repo R]` | Takes files, not symbols; files auto-detected when omitted. |
| Relationships | `query <pattern> <target> [--repo R]` | Patterns: `callers_of`, `callees_of`, `imports_of`, `importers_of`, `children_of`, `tests_for`, `inheritors_of`, `file_summary`. |
<<<<<<< HEAD
| Search | `search <query> [--kind File\|Class\|Function\|Type\|Test] [--limit N]` | |
| Dead code | `dead-code [--kind Function\|Class] [--file-pattern P] [--limit N] [--json]` | Hints only (`refactor.py` caveats). |
| Refactor preview | `refactor {rename,dead_code,suggest} [--old-name] [--new-name] [--kind] [--path]` | CLI prints a preview; apply exists only as MCP `apply_refactor_tool` within 600 s of the preview (`refactor.py`). |
| Drop files | `forget PATH... [--dry-run]` | Removes parsed files without a rebuild. |
| Watch one repo | `watch [--repo R] [--data-dir D]` | Filesystem events, 1 s debounce; requires an existing graph. |
| Registry | `register <path> [--alias A]`, `unregister <path\|alias>`, `repos` | `register` has no data-dir flag; `--data-dir` on `build`, `update`, `postprocess`, `embed`, `forget`, or `dead-code` writes the registry `data_dir`; on read-only `status`/`watch`/`detect-changes` it only selects the database (`cli.py`). |
| Cleanup | `prune [--apply] [--data-dirs] [--config watch.toml]` | Report only unless `--apply`; `--data-dirs` also deletes orphaned external data dirs. |
| MCP server | `serve [--repo R] [--auto-watch] [--tools all\|lean\|<csv>] [--detail minimal\|standard\|verbose] [--http --host --port]`; `mcp [--repo R] [--auto-watch]` | stdio by default; `--http` binds 127.0.0.1:5555. `mcp` accepts no tools/detail/http flags. |
| Daemon | `daemon {start [--foreground], stop, restart, status, logs [--repo ALIAS] [--follow] [--lines N], add <path> [--alias A], remove <path\|alias>}` | `crg-daemon` exposes the same verbs. |
=======
| Search | `search <query> [--kind File\|Class\|Function\|Type\|Test] [--limit N] [--repo R]` | |
| Dead code | `dead-code [--kind Function\|Class] [--file-pattern P] [--limit N] [--json] [--repo R]` | Hints only (`refactor.py` caveats). |
| Refactor preview | `refactor {rename,dead_code,suggest} [--old-name] [--new-name] [--kind] [--path] [--repo R]` | CLI prints a preview. Apply exists only as MCP `apply_refactor_tool` for a preview held in the same server process for at most 600 s (`refactor.py`); fleet renames never use it. |
| Drop files | `forget PATH... [--dry-run] [--repo R]` | Removes parsed files without a rebuild. |
| Watch one repo | `watch [--repo R] [--data-dir D]` | Filesystem events, 1 s debounce; exits 1 without a graph. |
| Registry | `register <path> [--alias A]`, `unregister <path\|alias>`, `repos` | Registry used by `list_repos_tool` and cross-repo search. |
| Cleanup | `prune [--apply] [--data-dirs] [--config watch.toml]` | Report only unless `--apply`; `--data-dirs` also deletes orphaned external data dirs. |
| MCP server | `serve [--repo R] [--auto-watch] [--tools all\|lean\|<csv>] [--detail minimal\|standard\|verbose] [--http --host --port]`; `mcp [--repo R] [--auto-watch]` | stdio by default; `--http` binds 127.0.0.1:5555. `mcp` accepts no tools/detail/http flags. |
| Daemon | `daemon {start [--foreground], stop, restart, status, logs [--repo ALIAS] [--follow] [--lines N], add <path> [--alias A], remove <path\|alias>}` | `crg-daemon` exposes the same verbs. |
| Projection | `install [--repo R] [--dry-run] [--no-skills] [--no-hooks] [--no-instructions] [-y] [--platform P]` | Upstream writer of MCP config, hooks, generated skills, and instruction blocks; AI Hub owns its use. |
>>>>>>> origin/dev

## Post-processing levels

`build` and `update` map flags to one level (`cli.py`): default `full`
(flows, communities, FTS); `--skip-flows` gives `minimal` (signatures and FTS);
`--skip-postprocess` gives `none`. The MCP `build_or_update_graph_tool`
<<<<<<< HEAD
accepts the same `postprocess` values. After a `minimal` or `none` build, run
`postprocess` before flow or community questions.
=======
accepts the same `postprocess` values. After a `minimal` or `none` run, run
`postprocess` before flow or community questions; embeddings refresh only
through `embed`.
>>>>>>> origin/dev

## Resolution and state

- Repository root (`incremental.py` `find_project_root`): `CRG_REPO_ROOT`,
  then the git top level, then the working directory. For the graph-tool
  commands (`query`, `impact`, `search`, `refactor`, ...) an explicit `--repo`
  resolves to the nearest `.git`, `.svn`, or `.code-review-graph` marker
  (`cli.py`).
- Data dir (`incremental.py` `get_data_dir`): registry `data_dir` for the
  resolved root, then `CRG_DATA_DIR`, then `<root>/.code-review-graph`; the
  database is `graph.db` inside it.
<<<<<<< HEAD
=======
- `--data-dir` on `build`, `update`, `postprocess`, `embed`, `forget`, or
  `dead-code` writes the registry `data_dir`; on read-only `status`, `watch`,
  `detect-changes`, `visualize`, or `wiki` it only selects the database
  (`cli.py`). `register` has no data-dir flag.
>>>>>>> origin/dev
- User state (`constants.py` `crg_home`): `CRG_HOME`, default
  `~/.code-review-graph`, holding `registry.json`, `watch.toml`, daemon state,
  and `logs/`.
- Ignore policy: `<root>/.code-review-graphignore`.

<<<<<<< HEAD
## Environment variables read by the code

| Variable | Effect (default) | Source |
| --- | --- | --- |
| `CRG_RECURSE_SUBMODULES` | `1`/`true`/`yes` adds `--recurse-submodules` to `git ls-files` in the full build file inventory (unset: off). Incremental `update` still uses `git diff --name-status <base>` of the root repository. | `incremental.py` |
| `CRG_DATA_DIR` | Graph data dir when the registry has no entry (unset: `<root>/.code-review-graph`). | `incremental.py` |
| `CRG_REPO_ROOT` | Overrides repository root detection. | `incremental.py`, `main.py` |
| `CRG_HOME` | Per-user state dir (unset: `~/.code-review-graph`). | `constants.py` |
| `CRG_TOOLS` | MCP tool filter when `--tools` is absent: `all`, `lean`, or CSV (unset: all). | `main.py` |
| `CRG_DETAIL_LEVEL` | Server-wide `minimal`/`standard`/`verbose` override when `--detail` is absent. | `main.py` |
| `CRG_GIT_TIMEOUT` | Git subprocess timeout seconds (30; doctor 10). | `incremental.py`, `changes.py`, `doctor.py` |
| `CRG_PARSE_WORKERS`, `CRG_SERIAL_PARSE` | Parse parallelism (min(cpu, 8)); `1` forces serial parsing. | `incremental.py` |
| `CRG_CHURN_WINDOW_DAYS` | Window for `detect-changes --churn` (90). | `changes.py` |
| `CRG_MAX_IMPACT_DEPTH`, `CRG_MAX_IMPACT_NODES` | Impact traversal bounds (2, 500). | `constants.py` |
| `CRG_ACCEPT_CLOUD_EMBEDDINGS` | `1` suppresses the cloud-egress warning for cloud embedding providers. | `embeddings.py` |

Other `CRG_*` tuning variables exist (watch scheduling, daemon restart backoff,
BFS limits); read the source before setting one.

## MCP

- `serve` exposes 30 tools by default. `--tools lean` keeps
  `get_minimal_context_tool`, `query_graph_tool`, `semantic_search_nodes_tool`,
  `detect_changes_tool`, `get_review_context_tool`, `get_impact_radius_tool`,
  `get_affected_flows_tool`.
- Start with `get_minimal_context_tool(task=...)`. `detail_level` defaults
  differ per tool (`get_review_context_tool`, `get_affected_flows_tool`,
  `list_flows_tool`, `list_communities_tool`, and `refactor_tool` default to
  `standard`); pass `detail_level="minimal"` explicitly and escalate only when
  it is insufficient. A server override (`--detail` or `CRG_DETAIL_LEVEL`)
  replaces every per-call value.
- Read results carry a `_graph` envelope (`built_at_sha`, `built_on_branch`,
  `head_sha`, `head_matches_build`). It compares commits only
  (`tools/_common.py`).
- `build_or_update_graph_tool` and `apply_refactor_tool` are writes; keep them
  under the same gate discipline as code changes.
- Claude Code reaches a stdio server through the project MCP config. ai-hub
  declares a project-scoped `code-review-graph serve` route that is currently
  disabled; a repository-local MCP entry written by `install` is not an ai-hub
  projection.

## Hooks written by `install` (Claude platform)

`install` merges into `<root>/.claude/settings.json` (`skills.py`):

- `PostToolUse` matcher `Edit|Write`: `code-review-graph update --skip-flows --repo "$(git rev-parse --show-toplevel)" || true` (timeout 30 s).
- `SessionStart`: `code-review-graph status --repo "$(git rev-parse --show-toplevel)"`.

Both exit silently when the binary is not on `PATH`, and `|| true` discards
update failures. In a submodule the top level is the member root, so the hook
updates the member graph, never the superproject graph. When hooks are absent
(`doctor` shows `hooks` unchecked), run the manual runbook steps instead of
installing them.

## Daemon

- The daemon reads `watch.toml` under `CRG_HOME`; each `[[repos]]` entry takes
  `path`, `alias`, and optional `data_dir`, `recurse_submodules`, `embedding`,
  exported to its watcher as `CRG_DATA_DIR`, `CRG_RECURSE_SUBMODULES=1`, and
  `CRG_EMBEDDING_MODEL` (`daemon.py`).
- It spawns `code-review-graph watch --repo <path>` per entry and runs one
  initial `build` for an entry without a database.
- When `watch.toml` carries a generated header, it is an ai-hub projection:
  change the workspace policy at its owner and resync; `daemon add|remove`
  would write into the projection.
- `daemon status` lists skipped entries whose directory no longer exists;
  `prune` reports them for removal.

## Doctor fixes

| Check | Symptom | Fix |
| --- | --- | --- |
| graph | no database | `build --repo <root>` (superproject: with `CRG_RECURSE_SUBMODULES=1`) |
| freshness | graph commit differs from HEAD | `update --brief`; `build` when `update` exits 1 |
| mcp-config, serve-cmd, server | missing or failing MCP entry | ai-hub MCP configuration finding; do not run `install` |
| hooks | no hooks detected | manual `update` after edits; hook projection is ai-hub owned |
| embeddings | none | optional; `embed` only when semantic search is required |
=======
Environment, MCP, install projections, watchers, and doctor fixes:
[runtime reference](runtime.md).
>>>>>>> origin/dev
