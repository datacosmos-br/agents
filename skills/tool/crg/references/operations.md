# crg operations reference

## Environment variables

| Variable | Default | Effect |
|---|---|---|
| `CRG_RECURSE_SUBMODULES` | off | `1`/`true`/`yes` adds submodule files to full builds; read at process start. |
| `CRG_DATA_DIR` | unset | Graph directory when the registry has no `data_dir` for the checkout. |
| `CRG_HOME` | user CRG home | Registry, logs, `watch.toml`, and default vstore root. |
| `CRG_TOOLS` | `all` | MCP tool set: `all`, `lean`, or a comma-separated list (same as `serve --tools`). |
| `CRG_DETAIL_LEVEL` | unset | Forces `minimal`/`standard`/`verbose` on every MCP tool. |
| `CRG_REPO_ROOT` | unset | Overrides root detection when no explicit root is given. |
| `CRG_SERIAL_PARSE` | off | `1` parses serially (diagnosis of parser crashes). |
| `CRG_PARSE_EXECUTOR` | `process` | `thread` or `process`; the stdio MCP server selects `thread`. |
| `CRG_GIT_TIMEOUT` | 30s (doctor 10s) | Git subprocess timeout. |
| `CRG_TOOL_TIMEOUT` | 0 (none) | Timeout for `detect_changes_tool`. |
| `CRG_MAX_WATCH_SCHEDULES` | 24 | Directory watch split cap before one recursive watch. |
| `CRG_VSTORE` | `$CRG_HOME/vstore` | Content-addressed bundle store for `build --seed-from`. |
| `CRG_ACCEPT_CLOUD_EMBEDDINGS` | unset | Acknowledges source upload to a cloud embedding provider. |

## Data-dir resolution

1. Registry `data_dir` for the checkout path.
2. `CRG_DATA_DIR`.
3. `<checkout>/.code-review-graph/` (self-ignoring directory).

Any mutating command given `--data-dir` (build, update, watch, status,
detect-changes, forget, visualize, wiki, dead-code) writes that location into
the registry; later runs reuse it without the flag.

## Command lifecycle

| Command | Use |
|---|---|
| `build` | Full re-parse. `--skip-flows`, `--skip-postprocess`, `--seed-from [STORE]`. |
| `update` | Changed files since the last built commit (`--base` overrides); `--brief` adds risk summary. |
| `postprocess` | Flows, communities, FTS on an existing graph (`--no-flows`, `--no-communities`, `--no-fts`). |
| `watch` | Initial incremental update, then filesystem watch for one checkout. |
| `daemon start/stop/restart/status/logs/add/remove` | Multi-checkout watchers from `watch.toml`. `add` takes `path` and `--alias`; per-repo `data_dir`, `recurse_submodules`, and `embedding` are TOML keys exported to each watcher. |
| `status [--json]` | Nodes, edges, branch, `built_at_sha`, last update. |
| `doctor` | Health checklist with next-step hints; exit 1 on a critical failure. |
| `register <path> [--alias]`, `unregister`, `repos`, `prune [--apply] [--data-dirs]` | Multi-repo registry used by `list_repos_tool` and cross-repo search. Aliases are not unique. |
| `serve [--repo] [--tools] [--detail] [--auto-watch] [--http --host --port]` | MCP server (stdio default). |

## MCP routing

- Per-call `repo_root` wins over `serve --repo`, which wins over the server cwd.
- The HTTP transport shares one default root; pass `repo_root` on every call
  when several checkouts are in use.
- `list_repos_tool` and `cross_repo_search_tool` read the registry.

## Hooks written by `install`

- Claude/Qoder settings: `PostToolUse` (`Edit|Write`) runs
  `update --skip-flows` and `SessionStart` runs `status`, both resolving the
  root with `git rev-parse --show-toplevel`.
- Codex: user-level hooks with the same two commands, using the cwd.
- Git `pre-commit`: `detect-changes`.
- Gemini: hook scripts and MCP `cwd` embed the absolute checkout path at
  install time; regenerate them per checkout.
- `install --dry-run` previews; `--no-hooks`, `--no-skills`,
  `--no-instructions`, `--platform <name>` narrow the writes.

## Doctor checks

| Check | Critical | Hint |
|---|---|---|
| graph database has nodes | yes | `build` |
| freshness (stored HEAD vs current) | no | `update` / `build` |
| repo-local MCP config present | no | `install` |
| serve launcher resolves | no | reinstall |
| server boots and counts tools | no | reinstall |
| pre-commit or Claude/Qoder hooks present | no | `install` |
| embeddings present | informational | `embed` |

Gemini and Codex hooks are not inspected by `doctor`.
