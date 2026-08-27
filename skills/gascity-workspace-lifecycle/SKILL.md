---
name: gascity-workspace-lifecycle
description: gascity, workspace, lifecycle, city, rig, pack, placement
bundle: governance
scope: personal
---

# Gas City Workspace Lifecycle

Use for choosing where Gas City-managed project work belongs. Read the
repository owner document `rules/gascity.md` before acting.

## Workflow

1. Inspect the declared city and its `city.toml`; do not infer configuration.
2. Verify the project is a registered rig before dispatching work.
3. Compose reusable behavior through explicit, pinned Pack V2 imports.
4. Route work to a declared agent and formula; inspect its run and session.
5. Use only the workspace selected by the rig/provider contract.

## Critical rules

- Never translate a `gt` command by changing its prefix to `gc`.
- Never invent `gc done`, `gc commit`, Refinery, crew, or polecat semantics.
- Never use a loose clone, ad-hoc worktree, `/tmp`, symlink, or cross-repo path.
- While runtime is suspended, document and validate statically; do not run `gc`.
