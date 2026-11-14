---
name: archify
description: architecture diagrams, codebase maps, sequence dataflow, explainers, interactive html
license: MIT
metadata:
  aihub.tags: '["activation:opt-in","decision:ADR-0038","detect:opt-in:archify","effective:2026-11-14","extends:arch-docs","route:agent","subject:architecture","usage:on-demand"]'
---

# archify

Archify turns a typed, validated intermediate representation (IR) into architecture
views: diagrams, codebase maps, sequence and dataflow views, explainers and interactive
HTML. It is a view layer under `$arch-docs`, which owns evidence, ownership and review;
code-review-graph (`$crg`) owns structural evidence. AI Hub installs the `archify` CLI;
read its schemas and references from its install directory, and `archify --help` owns
the grammar. This skill ships no runtime files.

## Create

1. Narrow the scope with CRG (CLI today; MCP when its route is re-enabled) under the
   `$crg` freshness gate: `architecture`, `flows`, `query importers_of|callers_of`.
2. Confirm every component and relation in source and record it as `file:line`; a
   graph result alone is never a fact.
3. Pin the revision: `git rev-parse HEAD` into `meta.repository.revision` and the
   credential-free `origin` URL into `meta.repository`. SSH or private origins get
   `link_mode: local-only`.
4. Write the IR at `docs/architecture/<view>.archify.json`, valid against the
   installed schema.

## Critique

- Run the archify gates on the IR and read the receipt.
- CRG cross-check: every component's source file is in the graph; every relation has a
  graph path or is marked `not statically visible`.
- A second agent reviews the view under `$arch-docs` before it lands.

## Improve

- Apply only the fixes the receipt lists in `supportedFixes`; never hand-patch output.
- Two improvement rounds at most; then stop and report what remains.
- Use `archify compare` to show the delta between rounds or revisions.

## Validate

- `archify finalize <ir> --repo-root <rig> --json` exits 0.
- The receipt revision equals `meta.repository.revision`; a mismatch means the view is
  stale and is regenerated, never edited.

## Boundaries

- No third-party brand marks in any view.
- Never edit provider instruction files (`CLAUDE.md`, `AGENTS.md`, provider homes).
- Changes to this procedure or the installed tool land only by an agents or ai-hub PR.

## Provenance

- Origin: <https://github.com/tt-a1i/archify> (v3.2.0)
- Commit: `208acba8d412335185b2056fedf54b3405df43fb`
- License: MIT
