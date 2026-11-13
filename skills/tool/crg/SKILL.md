---
name: crg
description:
  "code-review-graph fleet contract, graph freshness, structural impact, worktree graphs"
metadata:
  aihub.tags: '["activation:opt-in","decision:ADR-0038","detect:opt-in:code-review-graph","effective:2026-11-03","route:agent","subject:mcp","usage:on-demand"]'
---

# crg

Every session maps code through code-review-graph (CRG) before reading files at random or
editing, then confirms the exact lines in source (tracker memory
`operator-ruling-20261022-crg-every-session`). Pick the verb the question needs
(`search`, `query callers_of|tests_for|importers_of`, `impact --files`, `architecture`,
`flows`, `large-functions`, `dead-code --json`, `detect-changes`); `--help` owns the
grammar. Invoke the binary directly, never through a project launcher such as `uv run`
that may resync the environment. AI Hub owns installation, watchers, MCP routing, hooks
and generated instruction surfaces.

## Freshness gate

- A result is evidence only when `status --json --repo <root>` reports `built_at_commit`
  equal to `current_sha` on the same branch, and an MCP result carries
  `_graph.head_matches_build: true` (absent means unknown, never fresh).
- Both compare commits: uncommitted edits count after `update`, untracked files once
  tracked. A stale graph gets `update --brief`, or `build` when `update` exits 1; edit
  hooks run `update --skip-flows`, so flows and communities wait for `postprocess`.
- Every result cited in a bead or PR carries its `built_at_commit`.

## Topology

- One graph per Git root. Every lane worktree gets its own graph, seeded from the fresh
  workspace graph (`vstore put --repo <workspace>`) or built for the lane, and one
  `watch --repo <lane>` for its whole life unless the host watcher already covers it.
  A copied graph that still names another checkout's files is never lane evidence.
- A superproject builds with `CRG_RECURSE_SUBMODULES=1`; `update` diffs only the root, so
  a member commit needs a recursive rebuild or the member's own graph.
- Data directories live in the registry and are never temporary. Before starting a
  watcher or daemon, check both the host watcher and `daemon status`; `watch.toml` is an
  AI Hub projection, so `daemon add|remove` never writes into it. A lane graph is built or
  updated before a generation verb, never during it.
- At retirement the lane watcher stops, the lane is unregistered, and `prune` is reviewed
  before `prune --apply`. With several checkouts, every MCP call passes `repo_root`.

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
