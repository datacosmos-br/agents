---
name: crg
description: 'code-review-graph, impact analysis, graph-backed refactor, submodule graph'
metadata:
  aihub.tags: '["activation:opt-in","decision:ADR-0014","detect:opt-in:crg","effective:2026-09-16","route:agent","subject:mcp","usage:on-demand"]'
---

# crg

code-review-graph (CRG) is the agent-side structural graph of a checkout:
callers, importers, tests, flows, impact radius, dead code, and rename
previews. It narrows scope before reading source and attaches blast-radius
evidence to tracker items and reviews. It is never a gate and never product
code: a project imports nothing from it.

This skill is the interim manual contract. The owning automation (governed
workspace sync, recursive serving, worktree data dirs, MCP enablement) belongs
to AI Hub's CRG autopilot; once that owner declares it closed, prefer its
generated surface and keep only the query workflow below.

## USE FOR

- Locating symbols, callers, importers, inheritors, and tests before a change.
- Estimating a change: `impact`, `detect-changes`, affected flows, test gaps.
- Planning a cascade: `refactor rename` preview, `dead-code`, `refactor suggest`
  before the project's own rewrite owner executes it.
- Keeping a lane's graph fresh: build, update, postprocess, watch, daemon.
- Diagnosing graph, MCP, registry, or hook setup with `doctor`.

## DO NOT USE FOR

- Gate or completion evidence: the project's canonical verbs decide; a graph
  result is a hypothesis to verify in source. An empty result can mean
  "not indexed" or "not statically visible", not "does not exist".
- Applying refactors in a repository that owns a rewrite engine (for example a
  `make mod` codemod/Rope surface): CRG previews, the owner applies.
- Importing `code_review_graph` from project code, or committing graph data.
- Hand-editing generated MCP configs, hooks, or injected instruction blocks;
  regenerate through `install` (or the AI Hub projection once it owns them).

## Workflow

1. **Resolve the checkout.** One graph per checkout path; a linked worktree
   never reuses the primary checkout's graph. Pass the checkout explicitly:
   `--repo <root>` on the CLI, `repo_root` on every MCP tool call.
2. **Health first.** `code-review-graph doctor --repo <root>`; exit 1 means a
   critical check failed (usually no graph). Then
   `code-review-graph status --repo <root> --json` and compare `built_at_sha`
   with `HEAD`.
3. **Build once per checkout.** A superproject with submodules must recurse:
   `CRG_RECURSE_SUBMODULES=1 code-review-graph build --repo <root>`.
   The variable is the only switch (no CLI flag). For a large first build,
   `--skip-flows` then `code-review-graph postprocess --repo <root>` separates
   parsing from flows/communities/FTS.
4. **Stay fresh.** After commits or merges:
   `code-review-graph update --repo <root> --brief` (re-parses changed files and
   prints the risk summary). Rebuild with the recurse variable after submodule
   gitlink moves, because incremental diffs do not walk into submodules.
   Long sessions: `CRG_RECURSE_SUBMODULES=1 code-review-graph watch --repo <root>`
   in a background job, or the daemon (see references).
5. **Query before reading.** `search <text> [--kind Class]`,
   `query <pattern> <target>` (`callers_of`, `importers_of`, `tests_for`,
   `inheritors_of`, `file_summary`), `impact --files <paths>`,
   `detect-changes --base <ref> --brief`, `large-functions`,
   `dead-code [--file-pattern <path>]`, `architecture`, `flows`.
6. **Refactor cascade.** `refactor rename --old-name <a> --new-name <b>`
   or `refactor suggest` (preview with edit list), review the edits, then apply
   through the repository's own rewrite owner; rerun `update --brief` and the
   canonical verbs afterwards.
7. **MCP.** When the session exposes the CRG MCP server, call the equivalent
   `*_tool` functions with `repo_root`; if it reports `not_built`, run step 3.
   `serve --tools lean` exposes the curated low-token set; `--auto-watch` keeps
   the served graph fresh.

## Critical rules

- `--data-dir` is persisted into the registry for that checkout; pass it only
  for the checkout that should own that location, never a temporary directory.
- Registry (`register`, `unregister`, `repos`, `prune`) is CRG-owned state;
  `prune` reports only until `--apply`, and `--data-dirs` deletes data.
- Hooks and MCP entries written by `install` must stay checkout-relative;
  an absolute repository path baked into a tracked hook or MCP config is a
  projection defect to fix at its generator, not to copy between checkouts.
- Cloud embedding providers transmit source-derived text; use them only with
  explicit authorization. Local FTS fallback is the default.

## Example

Superproject lane after merging the integration tip:

1. `code-review-graph doctor --repo "$PWD"` → `graph: no nodes` (critical).
2. `CRG_RECURSE_SUBMODULES=1 code-review-graph build --repo "$PWD"` → files,
   nodes, and edges reported; `status --json` shows `built_at_sha == HEAD`.
3. `code-review-graph impact --repo "$PWD" --files <changed files>` →
   impacted callers and test gaps attached to the tracker item.
4. `code-review-graph refactor rename --old-name <old> --new-name <new>
   --kind Class --repo "$PWD"` → preview; the repository codemod owner
   applies it; `update --brief` confirms zero dangling references; canonical
   verbs validate.

## Troubleshooting

- `not_built` / zero nodes after "up to date": the incremental path found no
  diff but no graph exists; run a full `build` (with the recurse variable).
- Submodule symbols missing: the build ran without `CRG_RECURSE_SUBMODULES=1`.
- Stale results in a worktree: a hook or MCP config targets another checkout's
  absolute path; `doctor` does not inspect every platform's hooks, so read the
  hook files and regenerate them with `install --repo <root>`.
- Slow or hung MCP analysis: bound `detect_changes_tool` with
  `CRG_TOOL_TIMEOUT`; narrow with `changed_files` and `max_results`.

Environment variables, data-dir resolution, daemon configuration, hook
templates, and doctor checks: `references/operations.md`.
