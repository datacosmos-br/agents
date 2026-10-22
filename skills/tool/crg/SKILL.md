---
name: crg
description:
  "code-review-graph fleet contract, graph freshness, structural impact, worktree graphs"
metadata:
  aihub.tags: '["activation:opt-in","decision:ADR-0010","detect:opt-in:code-review-graph","effective:2026-10-22","route:agent","subject:mcp","usage:on-demand"]'
---

# crg

Every session maps code through code-review-graph (CRG) before reading files at random
or editing. The operator selected it for all sessions (tracker memory
`operator-ruling-20261022-crg-every-session`). Use it for structural evidence after
proving that the graph belongs to the current checkout and commit. AI Hub owns
installation, watcher lifecycle, MCP routing, hooks, and generated instruction surfaces. Query technique belongs to the
generated CRG skills; verified commands and runtime details live in the
[operations](references/operations.md) and [runtime](references/runtime.md) references.

## Map first

After the freshness gate below, start every exploration, review, refactor and
consolidation with the graph, then confirm in source. Every verb takes `--repo <root>`:

| Need | Verb |
|---|---|
| Find a function, class, file or test by name | `search "<name>" [--kind Function\|Class\|File\|Test]` |
| Callers, callees, imports, importers, children, tests, subclasses | `query callers_of\|callees_of\|imports_of\|importers_of\|children_of\|tests_for\|inheritors_of\|file_summary <target>` |
| Blast radius of a change | `impact --files <changed...> [--depth N] [--base <sha>]` |
| Module map and communities | `architecture [--detail-level minimal\|standard]`, `communities [--sort size\|cohesion\|name]`, `community --id <id>\|--name <name> [--members]` |
| Execution paths | `flows [--sort criticality\|depth\|node_count\|file_count\|name]`, `flow --id <id>\|--name <name> [--source]` |
| Oversized units to reduce | `large-functions [--min-lines N] [--kind Function\|Class\|File\|Test]` |
| Unreferenced code candidates | `dead-code --json [--kind Function\|Class] [--file-pattern <s>]` |
| Rename, dead-code and suggestion previews | `refactor rename\|dead_code\|suggest [--old-name] [--new-name]` (preview only) |
| Change risk for a review | `detect-changes --brief [--base <ref>]` |
| Browsable documentation of the graph | `wiki [--force]` |

Grep and file reads confirm exact lines and the facts the graph cannot express
(attribute access inside expressions, YAML-loaded models); they never replace the map.
A delegated mapping or refactor-discovery assignment names CRG as its primary tool,
carries the freshness result, and returns the CRG commands it ran.

## Use for

- Mapping owners, consumers, duplication and size before any change.
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

## Lane graph and watch (every worktree, always)

The operator ruled that every lane worktree starts from a copy of the workspace graph
and keeps a background watch for its whole life (tracker memory
`operator-ruling-20261022-crg-every-session`).

1. Workspace: pass the freshness gate on the workspace checkout, then
   `vstore put --repo <workspace>` stores its graph under the workspace `HEAD^{tree}`.
2. Lane: materialize that bundle into the lane and `update --brief --repo <lane>`.
   Graphs store absolute paths, so a copy names the workspace files: `update` refuses
   it ("built with a different repository root") and `build --seed-from` reports
   "Seeded" while leaving an empty graph. Until the owner rebases the stored root
   (aihub-l42it.15, aihub-epvst), run `build --repo <lane>` and record the gap;
   never cite a copied graph as lane evidence.
3. Watch: keep exactly one `watch --repo <lane>` running in the background from seed to
   retirement, unless `ai-hub-watch.service` or `daemon status` already watches that
   graph (aihub-kvx0x.8). Its log must report the lane root as watched.
4. Retirement: stop the lane watcher, `unregister` the lane, and review `prune` before
   `prune --apply`.

Data-directory resolution is registry, then configured environment, then
`<lane>/.code-review-graph` ([operations](references/operations.md)). When neither the
registry nor the environment names one, the graph lands inside the checkout. Generators that verify directory membership then fail mid-run
(`make gen`: "source directory membership changed ... added=['.code-review-graph']").
Until AI Hub registers lane graphs with an external data directory (aihub-o93c3), build
and update the lane graph before a generation verb, never during it, and record the gap.

## Workspace topology

- One graph per git root; a linked lane worktree owns its own graph. Never read
  another checkout's graph as lane evidence.
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

## Minimal runbook

1. Start with `doctor --repo <root>` and the freshness gate; seed and watch the lane.
2. Before structural edits, use `impact --files`, `query callers_of|tests_for`, and
   `dead-code --json`, then confirm candidates in source.
3. After edits, confirm the watcher updated the graph and trust `status`, not a silent
   hook.
4. After landing, update the integration graph and recursively rebuild the superproject
   after gitlink rollups.
5. At lane retirement, follow step 4 of the lane section.
