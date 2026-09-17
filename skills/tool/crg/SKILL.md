---
name: crg
description: 'code-review-graph fleet contract, graph freshness, structural impact, worktree graphs'
metadata:
  aihub.tags: '["activation:opt-in","decision:ADR-0010","detect:opt-in:code-review-graph","effective:2026-09-16","route:agent","subject:mcp","usage:on-demand"]'
---

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

1. `code-review-graph status --json --repo <root>` must report
   `built_at_commit == current_sha` and matching branches.
2. MCP read results must carry `_graph.head_matches_build: true`; an absent
   envelope is unknown, not fresh.
3. On mismatch, run `update --brief --repo <root>`; if it exits 1 because no
   usable graph/base exists, run `build --repo <root>`.
4. Uncommitted changes require `update`; untracked files require tracking or a
   rebuild. Record the built commit with cited results.

## Topology and limits

- Every linked worktree/member has its own graph. Never cite a different
  checkout's graph as lane evidence.
- After member landing, rebuild the superproject with
  `CRG_RECURSE_SUBMODULES=1 code-review-graph build --repo <workspace-root>`;
  incremental updates see the member only as a gitlink.
- Static analysis misses dynamic dispatch and may misclassify callbacks,
  registry-loaded models, and annotation-only references. Confirm candidates in
  source, tests, and config before editing.

## Minimal runbook

1. Start with `doctor --repo <root>` and the freshness gate.
2. Before structural edits, use `impact --files`, `query callers_of|tests_for`,
   and `dead-code --json`, then confirm candidates in source.
3. After edits, update the same checkout and trust `status`, not a silent hook.
4. After landing, update the integration graph and recursively rebuild the
   superproject after gitlink rollups.
5. At lane retirement, `unregister` it and review `prune` before `prune --apply`.
