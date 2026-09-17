---
name: crg
description: 'code-review-graph fleet contract, graph freshness, structural impact, worktree graphs'
metadata:
  aihub.tags: '["activation:opt-in","decision:ADR-0010","detect:opt-in:code-review-graph","effective:2026-09-16","route:agent","subject:mcp","usage:on-demand"]'
---

<<<<<<<<< Temporary merge branch 1
# crg

Use code-review-graph (CRG) for structural evidence after proving that the graph
belongs to the current checkout and commit. AI Hub owns installation, watcher
lifecycle, MCP routing, hooks, and generated instruction surfaces. Query
technique belongs to the generated CRG skills; verified commands and runtime
details live in the [operations](references/operations.md) and
[runtime](references/runtime.md) references.

## Use for

- Freshness and provenance decisions before citing graph results.
- Impact, caller, test, and residue discovery before structural changes.
- Worktree, member, and recursive superproject graph topology.
- Watcher and `doctor` diagnosis through the declared AI Hub owner.

## Do not use for

- A known literal at a known location: read or grep it.
- Proof of absence: empty means not indexed or not statically visible.
- Mutation: renames and deletions land through the project codemod owner
  (`make mod`), never MCP `apply_refactor_tool`.
- Setup or repair with `install`/`uninstall`, or direct edits to managed MCP,
  hook, skill, daemon, and instruction projections.

## Ownership

- AI Hub installs the binary, supervises one watcher per graph, renders
  `watch.toml` and ignore policy, and owns MCP and instruction projections.
- Check the host watcher and CRG daemon before starting any watcher or daemon.
- Resolve repository roots with `--repo`; use registry-owned data directories,
  never temporary `--data-dir` values or hardcoded machine paths.
- Treat a missing binary, disabled route, or absent hook as an AI Hub owner
  defect. Cloud embeddings require explicit authorization.

## Freshness gate

1. `code-review-graph status --json --repo <root>` must show
   `built_at_commit == current_sha` and `built_on_branch == current_branch`.
<<<<<<<<< Temporary merge branch 1
   MCP read results carry a `_graph` envelope whose `head_matches_build` must
   be `true` (absent means provenance unknown, never fresh).
2. Both compare commits only. Uncommitted edits count only after `update`;
   untracked files are not seen until tracked or rebuilt.
3. Mismatch: `update --brief`. `update` exits 1 with no graph or no usable
   base commit; then `build`. Edit hooks run `update --skip-flows`, so flows
   and communities stay stale until `postprocess`.
4. Record `built_at_commit` with every result cited in a bead or PR.

## Workspace topology

- One graph per git root; a linked lane worktree builds its own
  (`build --repo <lane-worktree>`). Never read another checkout's graph as
  lane evidence.
- Superproject: `CRG_RECURSE_SUBMODULES=1 code-review-graph build --repo
  <workspace-root>`. The variable affects the full build only; `update` diffs
  the root repository, where a member is one gitlink, so member commits need
  a recursive rebuild or the member's own graph.
- `--data-dir` on `build`, `update`, `postprocess`, `embed`, `forget`, or
  `dead-code` is persisted into the registry; never pass a temporary dir.

## Limits (the source always wins)

- Static edges only: dynamic dispatch, registry or YAML-loaded models,
  annotation-only references, and callback protocols (libcst `leave_*`,
  `on_*`) can surface as false dead code.
- Confirm every deletion candidate in source, tests, and config; a
  graph-versus-grep disagreement is a finding, never a green.

## Reading `doctor`

`doctor --repo <root>` exits non-zero only for a missing or empty graph or an
MCP server import failure. Freshness, MCP config, and hooks are warnings. Its
hook check reads only `.git/hooks/pre-commit` and Claude/Qoder settings, so it
ignores `core.hooksPath`, linked worktrees, and Gemini/Codex hooks; its
`install` hints are owner findings, not agent actions.

## Manual runbook until AI Hub automation is live

1. Session start: `doctor --repo <root>`, then the freshness gate.
2. Before a structural refactor: `update --brief`, then `impact --files`,
   `query`, `dead-code --json`; record the built commit.
3. After edits: `update --repo <root>`; trust `status`, not the silent hook.
4. After landing: `update` in the integration checkout; rebuild the
   superproject graph recursively after gitlink rollups.
5. Lane retirement: `unregister <lane-worktree>`, then review `prune` before
   `prune --apply`.
=========
   MCP read results carry a `_graph` envelope; `head_matches_build` must be
   `true` (absent means provenance is unknown, never fresh).
2. That check compares commits only. Uncommitted edits count only after
   `update`, which diffs the working tree against the last built commit;
   untracked files are not seen until tracked or rebuilt.
3. Mismatch: `update --brief`. `update` exits 1 when no graph or no usable
   base commit exists; then run `build`. Record `built_at_commit` with every
   impact, query, or dead-code result cited in a bead or PR.

## Limits (the source always wins)

- Static edges only. Dynamic dispatch, registry or YAML-loaded models,
  annotation-only references, and callback protocols (libcst `leave_*`,
  `on_*`) can surface as false dead code. The detector exempts only `visit_*`,
  known prefixes, and framework bases (`BaseModel`, `BaseSettings`,
  `Protocol`, `ABC`, ...).
- Confirm every deletion candidate in source, tests, and config before acting;
  a graph-versus-grep disagreement is a finding, never a green.

## Workspace topology

- One graph per repository root: `--repo`, else `CRG_REPO_ROOT`, else the git
  top level. Its data dir: registry `data_dir`, else `CRG_DATA_DIR`, else
  `<root>/.code-review-graph`.
- Superproject: `CRG_RECURSE_SUBMODULES=1 code-review-graph build --repo <workspace-root>`
  indexes member files. The variable affects the full build only; `update`
  diffs the superproject, where a member is one gitlink, so member edits need
  a superproject rebuild or the member's own graph.
- Member or lane worktree: its own git root, its own graph. Build once inside
  it (`build --repo <lane-worktree>`); `--data-dir <dir>` also records that dir
  in the registry. Never read another checkout's graph as lane evidence.
- Registry: `repos`, `register <path> [--alias A]`, `unregister <path|alias>`,
  `prune` (report only; `--apply`, `--data-dirs`).

## Manual runbook until ai-hub automation is live

1. Session start: `doctor --repo <root>` (exit 1 on a critical check), then
   the freshness gate.
2. Before a structural refactor: `update --brief`, then `impact --files`,
   `query`, `dead-code --json`; record the built commit.
3. After edits: `update --repo <root>`. Edit hooks append `|| true` and fail
   silently; trust `status`, not the hook.
4. After landing: `update` in the integration checkout; rebuild the
   superproject graph with `CRG_RECURSE_SUBMODULES=1` after gitlink rollups.
5. Lane retirement: `unregister <lane-worktree>`, then `prune` and review its
   report before `prune --apply`.

## Ownership boundary

- ai-hub installs the binary, renders the daemon inventory (`watch.toml`) and
  the `.code-review-graphignore` policy block, and owns MCP and hook
  projection. Never hand-edit those projections or install a parallel CRG.
- Never hardcode machine paths: resolve roots with `--repo`, data dirs through
  the registry or `CRG_DATA_DIR`, and user state through `CRG_HOME`.
- A missing binary, disabled MCP route, or absent hook is an ai-hub
  configuration finding to file, not a reason to substitute another index.
>>>>>>>>> Temporary merge branch 2
