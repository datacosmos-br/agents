# code-review-graph operations reference

Verified against `code-review-graph 2.3.8+dc.3` (the AI Hub `dc-use` fork
build): each fact below comes from `code-review-graph <sub> --help` or the
installed package source named in parentheses. Re-verify with `--help` after
any version change; the help output wins over this page.

## Command surface

| Need | Command | Notes |
| --- | --- | --- |
| Health checklist | `doctor [--repo R]` | Checks graph, freshness, mcp-config, serve-cmd, server, hooks, embeddings; exit 1 only on a critical failure (`doctor.py`). |
| Stats and provenance | `status [--repo R] [--json] [--data-dir D]` | JSON keys `built_on_branch`, `built_at_commit`, `current_branch`, `current_sha`. Plain output warns on a branch mismatch only. Exits 1 when no graph exists (`cli.py`). |
| Full build | `build [--repo R] [--skip-flows] [--skip-postprocess] [--data-dir D] [--seed-from [STORE]] [-q]` | Re-parses every tracked file. |
| Incremental update | `update [--base B] [--repo R] [--brief] [--skip-flows] [--skip-postprocess] [--data-dir D] [-q]` | Default base is the stored built commit. Exits 1 with no graph or no usable base (`tools/build.py`). `--brief` also prints the risk summary. |
| Post-processing only | `postprocess [--repo R] [--no-flows] [--no-communities] [--no-fts] [--data-dir D]` | Recomputes signatures, FTS, flows, and communities on an existing graph (`postprocessing.py`). |
| Embeddings | `embed [--repo R] [--provider local\|openai\|google\|minimax\|voyage] [--model M] [--data-dir D]` | `local` needs the `embeddings` extra; without embeddings search uses FTS5. |
| Change analysis | `detect-changes [--base B] [--brief] [--repo R] [--churn]` | Read-only; default base `HEAD~1`; never re-parses. |
| Impact | `impact [--files F...] [--depth N] [--max-results N] [--base B] [--repo R]` | Takes files, not symbols; files auto-detected when omitted. |
| Relationships | `query <pattern> <target> [--repo R]` | Patterns: `callers_of`, `callees_of`, `imports_of`, `importers_of`, `children_of`, `tests_for`, `inheritors_of`, `file_summary`. |
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

## Post-processing levels

`build` and `update` map flags to one level (`cli.py`): default `full`
(flows, communities, FTS); `--skip-flows` gives `minimal` (signatures and FTS);
`--skip-postprocess` gives `none`. The MCP `build_or_update_graph_tool`
accepts the same `postprocess` values. After a `minimal` or `none` run, run
`postprocess` before flow or community questions; embeddings refresh only
through `embed`.

## Resolution and state

- Repository root (`incremental.py` `find_project_root`): `CRG_REPO_ROOT`,
  then the git top level, then the working directory. For the graph-tool
  commands (`query`, `impact`, `search`, `refactor`, ...) an explicit `--repo`
  resolves to the nearest `.git`, `.svn`, or `.code-review-graph` marker
  (`cli.py`).
- Data dir (`incremental.py` `get_data_dir`): registry `data_dir` for the
  resolved root, then `CRG_DATA_DIR`, then `<root>/.code-review-graph`; the
  database is `graph.db` inside it.
- `--data-dir` on `build`, `update`, `postprocess`, `embed`, `forget`, or
  `dead-code` writes the registry `data_dir`; on read-only `status`, `watch`,
  `detect-changes`, `visualize`, or `wiki` it only selects the database
  (`cli.py`). `register` has no data-dir flag.
- User state (`constants.py` `crg_home`): `CRG_HOME`, default
  `~/.code-review-graph`, holding `registry.json`, `watch.toml`, daemon state,
  and `logs/`.
- Ignore policy: `<root>/.code-review-graphignore`.

Environment, MCP, install projections, watchers, and doctor fixes:
[runtime reference](runtime.md).
