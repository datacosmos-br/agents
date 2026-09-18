---
name: crg
description:
  "code-review-graph fleet contract, graph freshness, structural impact, worktree graphs"
metadata:
  aihub.tags: '["activation:opt-in","decision:ADR-0010","detect:opt-in:code-review-graph","effective:2026-09-16","route:agent","subject:mcp","usage:on-demand"]'
---

# crg

Use code-review-graph (CRG) for structural evidence after proving that the graph belongs
to the current checkout and commit. AI Hub owns installation, watcher lifecycle, MCP
routing, hooks, and generated instruction surfaces. Query technique belongs to the
generated CRG skills; verified commands and runtime details live in the
[operations](references/operations.md) and [runtime](references/runtime.md) references.

## Use for

- Freshness and provenance decisions before citing graph results.
- Impact, caller, test, and residue discovery before structural changes.
- Worktree, member, and recursive superproject graph topology.
- Watcher and `doctor` diagnosis through the declared AI Hub owner.

## Do not use for

- A known literal at a known location: read or grep it.
- Proof of absence: empty means not indexed or not statically visible.
- Mutation: renames and deletions land through the project codemod owner (`make mod`),
  never MCP `apply_refactor_tool`.
- Setup or repair with `install`/`uninstall`, or direct edits to managed MCP, hook,
  skill, daemon, and instruction projections.

## Ownership

- AI Hub installs the binary, supervises one watcher per graph, renders `watch.toml` and
  ignore policy, and owns MCP and instruction projections.
- Check the host watcher and CRG daemon before starting any watcher or daemon.
- Resolve repository roots with `--repo`; use registry-owned data directories, never
  temporary `--data-dir` values or hardcoded machine paths.
- Treat a missing binary, disabled route, or absent hook as an AI Hub owner defect.
  Cloud embeddings require explicit authorization.

## Freshness gate

1. `code-review-graph status --json --repo <root>` must report
   `built_at_commit == current_sha` and matching branches.
2. MCP read results carry a `_graph` envelope whose `head_matches_build` must be `true`
   (absent means provenance unknown, never fresh).
3. Both compare commits only. Uncommitted edits count only after `update`; untracked
   files are not seen until tracked or rebuilt.
4. Mismatch: `update --brief`. `update` exits 1 with no graph or no usable base commit;
   then `build`. Edit hooks run `update --skip-flows`, so flows and communities stay
   stale until `postprocess`.
5. Record `built_at_commit` with every result cited in a bead or PR.

## Workspace topology

- One graph per git root; a linked lane worktree builds its own
  (`build --repo <lane-worktree>`). Never read another checkout's graph as lane
  evidence.
- Superproject:
  `CRG_RECURSE_SUBMODULES=1 code-review-graph build --repo <workspace-root>`. The
  variable affects the full build only; `update` diffs the root repository, where a
  member is one gitlink, so member commits need a recursive rebuild or the member's own
  graph.
- `--data-dir` on `build`, `update`, `postprocess`, `embed`, `forget`, or `dead-code` is
  persisted into the registry; never pass a temporary dir.

## Limits (the source always wins)

- Static edges only: dynamic dispatch, registry or YAML-loaded models, annotation-only
  references, and callback protocols (libcst `leave_*`, `on_*`) can surface as false
  dead code.
- Confirm every deletion candidate in source, tests, and config; a graph-versus-grep
  disagreement is a finding, never a green.

## Reading `doctor`

`doctor --repo <root>` exits non-zero only for a missing or empty graph or an MCP server
import failure. Freshness, MCP config, and hooks are warnings. Its hook check reads only
`.git/hooks/pre-commit` and Claude/Qoder settings, so it ignores `core.hooksPath`,
linked worktrees, and Gemini/Codex hooks; its `install` hints are owner findings, not
agent actions.

## Topology and limits

- Every linked worktree/member has its own graph. Never cite a different checkout's
  graph as lane evidence.
- After member landing, rebuild the superproject with
  `CRG_RECURSE_SUBMODULES=1 code-review-graph build --repo <workspace-root>`;
  incremental updates see the member only as a gitlink.
- Static analysis misses dynamic dispatch and may misclassify callbacks, registry-loaded
  models, and annotation-only references. Confirm candidates in source, tests, and
  config before editing.

## Minimal runbook

1. Start with `doctor --repo <root>` and the freshness gate.
2. Before structural edits, use `impact --files`, `query callers_of|tests_for`, and
   `dead-code --json`, then confirm candidates in source.
3. After edits, update the same checkout and trust `status`, not a silent hook.
4. After landing, update the integration graph and recursively rebuild the superproject
   after gitlink rollups.
5. At lane retirement, `unregister` it and review `prune` before `prune --apply`.
