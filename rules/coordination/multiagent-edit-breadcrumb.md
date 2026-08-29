---
globs: ["**/*.py", "**/*.md", "**/*.toml", "**/*.yaml", "**/*.yml"]
---

# Coordinate shared-file edits; never clobber WIP

Multiple agents may edit the same files concurrently. Declare file ownership in
the active collaboration channel before editing; do not add coordination-only
comments to product code or documentation.

The complete preservation, fix-forward, and severe-conflict contract is owned by
[fix-forward collaboration](fix-forward-collaboration.md).

- Re-read a mutable file right before editing; converge, never revert another
  actor's valid change.
- Never overwrite or stash uncommitted WIP. Preserve durable evidence in the next
  canonical commit/PR/CI artifact.
- Resolve the tracker mode from the repository's own instructions before any
  tracker action; while that authority declares suspension, invoke no tracker
  command, create no substitute tracker or ledger, and keep phase closure
  unavailable.
