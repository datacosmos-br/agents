---
name: safe-delete
description: 'safe deletion, artifact retirement, recovery evidence'
license: MIT
metadata:
  aihub.tags: '["provenance:agents-owned","role:governance","updates:manual","usage:on-demand"]'
  version: 2.0.0
---

# Safe Delete

Delete only exact, owned targets with an explicit recovery contract.

## Procedure

1. Resolve every literal target and classify it as tracked source, declared
   generated output, tool-owned transient data, or unknown/concurrent work.
2. Inspect references, repository status, open handles or locks, special file
   types, and the canonical owner before mutation.
3. Preserve unknown, dirty, locked, live, database, symlink, and special-file
   content in place. Escalate the exact blocker; never infer ownership by name.
4. Remove generated output only through its declared cleanup primitive.
5. Remove tracked superseded files through the scoped patch or version-control
   deletion only when complete cutover is the approved change and every consumer
   is rewired in the same cycle. Do not retain a sibling old copy.
6. For approved untracked material that requires recovery, move the exact target
   atomically to the repository's declared same-filesystem quarantine or trash.
   If none exists, stop for an approved destination.
7. Verify the intended target is absent from the active surface, preserved items
   remain intact, the repository diff is scoped, and native gates are green.

## Rules

- Never use recursive broad deletion, unresolved variables or globs, `git clean`,
  destructive reset, global stash, or force deletion.
- Never stage backups, workspaces, repositories, databases, or reports in `/tmp`.
- Never create `.bak`/`.bkp` siblings that leave old and new implementations active.
- Report what moved or was removed, its recovery location or irreversibility, and
  the exact validation evidence.
