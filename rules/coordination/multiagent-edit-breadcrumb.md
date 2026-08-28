---
globs: ["**/*.py", "**/*.md", "**/*.toml", "**/*.yaml", "**/*.yml"]
---

# Coordinate shared-file edits; never clobber WIP

Multiple agents may edit the same files concurrently. Declare file ownership in
the active collaboration channel before editing; do not add coordination-only
comments to product code or documentation.

- Re-read a mutable file right before editing; converge, never revert another
  actor's valid change.
- Never overwrite uncommitted WIP. Preserve durable evidence in the next
  canonical commit/PR/CI artifact.
- Tracker runtime is suspended. Invoke no tracker command and create no
  substitute ledger; phase closure remains unavailable.
