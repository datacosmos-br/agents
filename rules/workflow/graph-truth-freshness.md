---
description: Refresh code-review-graph before trusting impact or dead-code data
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-09-11","route:both"]'
---

# A stale graph is worse than no graph

`code-review-graph status` warns when the graph was built on a different
branch or commit than the working tree. In the cosmos fleet the registered
graphs last built on `fix/flext-pair-coherent-repin@b68347b7` (2026-09-07)
while lanes moved to `0.12.0-dev` and `develop` — any `impact`, `dead-code`,
or `refactor rename` verdict from that graph silently claims facts about
code that no longer exists.

- Before any graph-backed reasoning run: `code-review-graph status`; if the
  warning names a different branch/commit, `code-review-graph update --brief`
  for incremental, or `code-review-graph build` after rewrites, scoped
  `--repo <root>`.
- Graph mutations (`refactor rename`) are writes: pair them with the same
  gate discipline as any code change (mutation is the verb default, scoped
  commit, gates on merged SHA). Prefer `impact`/`dead-code`/`search`
  (read-only) as decision
  inputs; emit rename lists, then land renames through the project's own
  tooling (ast-grep rules, `make mod`), not by graph-side edit.
- `dead-code --json` and `impact --files <changed>` are the cheap pre-cost
  tables that make operator decisions concrete; treat them as needing the
  same ruler-freeze discipline as validator counts (record the commit).

See also: `runtime-is-reality.md` (rule file), `fresh-import` guards.
