---
description: Refresh code-review-graph before trusting impact or dead-code data
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-09-11","route:both"]'
---

# A stale graph is worse than no graph

`code-review-graph status --json` reports the commit and branch the graph was built at
(`built_at_commit`, `built_on_branch`) beside the working tree's (`current_sha`,
`current_branch`). When they differ — for example a registered graph last built on an
older fix branch while lanes moved to their integration branch — any `impact`,
`dead-code`, or `refactor rename` verdict from that graph silently claims facts about
code that no longer exists.

- Before any graph-backed reasoning run: `code-review-graph status --json`; if the built
  commit or branch differs, `code-review-graph update --brief` for incremental, or
  `code-review-graph build` after rewrites or when `update` exits 1, scoped
  `--repo <root>` (operation per the `crg` skill).
- CLI `refactor rename` only previews; the graph-side write is the MCP
  `apply_refactor_tool`. Never use that apply path: take
  `impact`/`dead-code`/`search`/`refactor` previews as read-only decision inputs, emit
  rename lists, then land renames through the project's own tooling (ast-grep rules,
  `make mod`) under the same gate discipline as any code change (scoped commit, gates on
  merged SHA).
- `dead-code --json` and `impact --files <changed>` are the cheap pre-cost tables that
  make operator decisions concrete; treat them as needing the same ruler-freeze
  discipline as validator counts (record the commit).

See also: `runtime-is-reality.md` (rule file), `fresh-import` guards.
