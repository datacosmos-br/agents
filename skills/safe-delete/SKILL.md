---
name: safe-delete
description: "Use archive-to-sibling instead of deleting. USE FOR: any removal request, retiring superseded artifacts, cleanup with recoverability. DO NOT USE FOR: git clean/reset/stash on shared trees; tool-owned transient caches."
license: MIT
metadata:
  bundle: "governance"
  scope: "universal"
  version: "1.0.0"
---


# Safe Delete

Deletion is destructive and often irreversible in a shared multi-agent workspace.
The operator law is **archive, do not delete** — move to a `.bak` sibling so any
lane can recover the work.

## Use for

- Any request to delete, remove, or clean up files or directories.
- Retiring superseded modules, configs, or generated artifacts.

## Do not use for

- Untracked transient caches the tool owns (e.g. `.dmypy.json`) — those may be
  left or removed by their tool.
- `git clean`/`git reset`/`git stash` on shared trees — ABSOLUTELY FORBIDDEN.

## Workflow

1. **List** the exact matches (`ls` / `Glob`); show them before acting.
2. **Archive**, do not delete: `mv <path> <path>.bak` (or `.bkp`). Directories
   the same way: `mv <dir> <dir>.bak`.
3. For tracked files prefer `git rm` in a scoped commit ONLY when the deletion is
   the intended change; otherwise archive.
4. **Confirm** the archived paths and report them.

## Critical rules

- Never `rm -rf`. Never destroy another lane's WIP.
- Preserve unknown/concurrent changes in place; fix forward.
- Archive is a net; the operator can purge `.bak` files later.
