---
globs: **/*.py, **/*.md, **/*.toml, **/*.yaml, **/*.yml
---

# Leave a breadcrumb when editing shared files; never clobber WIP

Multiple agents edit the same files concurrently. On any shared-file edit, add a
short inline comment stating the intent for the other agent
(e.g. `# Why: purified so foundation does not import c/t/p/m/u`).

- Re-read a mutable file right before editing; converge, never revert another
  lane's change.
- Never overwrite another lane's uncommitted WIP. Record progress on the active
  bead with `bd update <id> --notes '...'`.
