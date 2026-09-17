# code-review-graph operations reference

Verified against `code-review-graph 2.3.8+dc.3` (the AI Hub `dc-use` fork).
Re-verify every command with `--help` after a version change; help output wins.

## Command surface

| Need | Command | Notes |
| --- | --- | --- |
| Health | `doctor [--repo R]` | Checks graph, freshness, MCP, server, hooks, and embeddings; owner warnings are not repair permission. |
| Provenance | `status [--repo R] [--json] [--data-dir D]` | Reports built/current branch and commit; exits 1 without a graph. |
| Full build | `build [--repo R] [--skip-flows] [--skip-postprocess] [--data-dir D] [--seed-from [STORE]] [-q]` | Re-parses tracked files. |
| Incremental update | `update [--base B] [--repo R] [--brief] [--skip-flows] [--skip-postprocess] [--data-dir D] [-q]` | Uses the stored built commit by default; exits 1 without a usable graph/base. |
| Post-process | `postprocess [--repo R] [--no-flows] [--no-communities] [--no-fts] [--data-dir D]` | Recomputes signatures, FTS, flows, and communities. |
| Embeddings | `embed [--repo R] [--provider local\|openai\|google\|minimax\|voyage] [--model M] [--data-dir D]` | Cloud providers require explicit authorization. |
| Change analysis | `detect-changes [--base B] [--brief] [--repo R] [--churn]` | Read-only; never reparses. |
| Impact | `impact [--files F...] [--depth N] [--max-results N] [--base B] [--repo R]` | Accepts changed files, not symbols. |
| Relationships | `query <pattern> <target> [--repo R]` | Supports callers, callees, imports, tests, inheritors, children, and file summary. |
| Search | `search <query> [--kind File\|Class\|Function\|Type\|Test] [--limit N] [--repo R]` | Keyword or embedding-backed. |
| Dead-code candidates | `dead-code [--kind Function\|Class] [--file-pattern P] [--limit N] [--json] [--repo R]` | Hints only; confirm in source. |
| Refactor preview | `refactor {rename,dead_code,suggest} [...] [--repo R]` | Preview only; fleet changes use the project codemod owner. |
| Drop files | `forget PATH... [--dry-run] [--repo R]` | Removes parsed files without rebuilding. |
| Watch one repo | `watch [--repo R] [--data-dir D]` | Requires an existing graph; never duplicate an active owner watcher. |
| Registry | `register <path> [--alias A]`, `unregister <path\|alias>`, `repos` | Registry entries own persistent graph locations. |
| Cleanup | `prune [--apply] [--data-dirs] [--config watch.toml]` | Report-only unless `--apply`; review first. |
| MCP | `serve [...]`; `mcp [--repo R] [--auto-watch]` | AI Hub owns the deployed route. |
| Daemon | `daemon {start,stop,restart,status,logs,add,remove}` | Check the AI Hub host watcher before effects. |
| Projection | `install [...]` | Upstream writer wrapped by AI Hub; agents never invoke it for repair. |

## Post-processing

Default build/update is full. `--skip-flows` produces minimal post-processing;
`--skip-postprocess` produces none. Run `postprocess` before flow/community
questions after either reduced mode. Refresh embeddings only through `embed`.

## Resolution and state

- Root: explicit `--repo`, then configured environment, then git root/current dir.
- Data: registry entry, then configured environment, then
  `<root>/.code-review-graph`; the database is `graph.db`.
- Mutating commands with `--data-dir` persist it in the registry; read-only
  commands only select it. Never use a temporary directory.
- User state contains the registry, `watch.toml`, daemon state, and logs.
- Ignore policy is `<root>/.code-review-graphignore`.

Environment, MCP, install projections, watchers, and doctor fixes are documented
in the [runtime reference](runtime.md).
