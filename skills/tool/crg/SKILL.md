---
name: crg
description: 'code-review-graph, structural impact, dead code, graph freshness, mcp graph tools'
metadata:
  aihub.tags: '["activation:opt-in","decision:ADR-0010","detect:opt-in:code-review-graph","effective:2026-09-16","route:agent","subject:mcp","usage:on-demand"]'
---

# code-review-graph (CRG)

CRG is the host structural index: a Tree-sitter graph (SQLite `graph.db`) that
answers callers, callees, imports, tests, impact, and dead-code questions.
ai-hub owns its installation, configuration, and index production (ADR-0010);
project code never imports it. This skill is the single canonical operating
guide until the ai-hub automation owners are live. Every command, flag, and
environment variable is verified in the
[operations reference](references/operations.md).

## USE FOR

- Structural questions: `query {callers_of,callees_of,imports_of,importers_of,children_of,tests_for,inheritors_of,file_summary} <target>`.
- Blast radius before structural or deletion-heavy edits: `impact --files <changed...>`,
  `detect-changes --brief`.
- Residue candidates: `dead-code --json`, `refactor dead_code|suggest`, and
  `refactor rename --old-name X --new-name Y` (a preview, never an edit).
- Review evidence: MCP `detect_changes_tool`, `get_review_context_tool`,
  `get_impact_radius_tool`, `get_affected_flows_tool`.

## DO NOT USE FOR

- A known literal at a known location: read or grep it.
- Proof of absence: an empty result means "not indexed or not statically
  visible", never "does not exist".
- Mutation: renames land through the project codemod owner (`make mod`),
  not through a graph-side apply.
- Repair by `code-review-graph install`: it rewrites repository MCP config,
  hooks, skills, and instruction files that ai-hub projects.

## Freshness gate (before any graph-backed claim)

1. `code-review-graph status --json --repo <root>` must show
   `built_at_commit == current_sha` and `built_on_branch == current_branch`.
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
