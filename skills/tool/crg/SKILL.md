---
name: crg
description:
  "code-review-graph fleet contract, graph freshness, structural impact, worktree graphs. USE FOR: searching the code graph, querying callers/callees/tests/importers, impact analysis, refactor preview, community wiki, dead-code and change detection, worktree graph readiness. DO NOT USE FOR: editing code, rebuilding the shared database manually, per-session collectors, or repairing AI Hub engines."
metadata:
  aihub.tags: '["activation:opt-in","decision:ADR-0038","detect:opt-in:code-review-graph","effective:2026-11-03","route:agent","subject:mcp","usage:on-demand"]'
---

# crg

Every session maps code through code-review-graph (CRG) before reading files at random or
editing, then confirms the exact lines in source (tracker memory
`operator-ruling-20261022-crg-every-session`). Pick the verb the question needs
(`search`, `query callers_of|tests_for|importers_of`, `impact --files`, `architecture`,
`flows`, `large-functions`, `dead-code --json`, `detect-changes`, `refactor`, `wiki`,
`context-history`); `--help` owns the grammar. The `dc-use` engine (`2.4.0+dc.5+`)
includes C3 MRO linearization, Python 3.13 typing, liveness-catalog dead-code precision,
non-code subjects, and `migrate-shared`. Invoke the binary directly, never through a
project launcher such as `uv run` that may resync the environment. AI Hub owns
installation, watchers, MCP routing, hooks and generated instruction surfaces.

> **Current vs target (2026-11-20).** Working checkouts share one native SQLite database
> (`shared.db` via `CRG_SHARED_DB`, ADR-0026 D12) indexed by one unified collector, with
> shared host embeddings (`ai-hub-embedding:latest`, 512d + task prefixes, ADR-0026 D11).
> Today AI Hub runs `ai-hub-watch.service` with `watch --manifest` and projects
> `watch.toml`. The accepted S4 target is one `ai-hub-maintain.service` owning a native
> `crg-daemon` child under an AI-Hub-owned `CRG_HOME`, retiring `ai-hub-watch.service`
> and the manifest. Do not treat S4 as already implemented.

**USE FOR:** mapping code before an edit; `search` / `query callers_of|tests_for|importers_of`;
`impact --files`; `architecture`; `flows`; `large-functions`; `dead-code --json`;
`detect-changes`; `refactor` preview; `wiki`; `context-history`; worktree graph readiness.

**DO NOT USE FOR:** editing or mutating code; rebuilding `shared.db` by hand; launching a
per-session collector or `update` loop; repairing AI Hub watch/maintain/MCP engines.

## Freshness gate

- A result is evidence only when `status --json --repo <root>` reports `built_at_commit`
  equal to `current_sha` on the same branch (`build_incomplete: false`), and an MCP
  result carries `_graph.head_matches_build: true` (absent means unknown, never fresh).
- Both compare commits: uncommitted edits count once indexed by the collector, untracked
  files once tracked. Never launch a second per-session collector or manual `update` loop
  against the shared database; wait for or inspect the unified collector, or run
  `postprocess` only on an isolated bundle.
- Every result cited in a bead or PR carries its `built_at_commit`.

## Topology

- One unified working collector over `CRG_SHARED_DB` (`shared.db`) indexes every selected
  workspace and linked worktree as native namespaces of that file. Per-worktree database
  copies (`vstore seed`) and per-session watchers are retired for working checkouts;
  immutable HEAD bundles retain their own isolated databases.
- A superproject builds with `CRG_RECURSE_SUBMODULES=1`; `update` diffs only the root, so
  a member commit needs a recursive rebuild or the member's own graph namespace.
- Data directories live in the registry and are never temporary. `watch.toml` is an AI
  Hub projection, so `daemon add|remove` never writes into it.
- At retirement the lane is unregistered and `prune` is reviewed before `prune --apply`
  (or `migrate-shared` for legacy shared generations). With several checkouts, every MCP
  call passes `repo_root`.

## Limits

- Edges are static: dynamic dispatch, registries, YAML-loaded models, annotation-only
  references and callback protocols can look dead. Every dead-code hit is confirmed in
  source, tests and config, and an empty result means not indexed, never absent.
- The graph never mutates code: `refactor` only previews, renames and deletions land
  through the project's codemod owner (`make mod` in FLEXT), and MCP
  `apply_refactor_tool` is never used. `wiki` writes only under the graph data directory.
- `doctor` fails only for a missing graph or an MCP import failure. Its `install` hints,
  a missing binary, a disabled route or an absent hook are AI Hub findings, never agent
  repairs. Cloud embeddings need explicit authorization.
