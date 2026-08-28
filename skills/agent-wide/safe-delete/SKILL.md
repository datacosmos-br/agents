---
name: safe-delete
description: 'safe deletion, atomic obsolete-code extermination, artifact retirement, recovery evidence'
license: MIT
metadata:
  aihub.tags: '["policy:atomic-effects","policy:causal-subprocess","policy:fail-loud","policy:no-fallback","policy:preflight-before-effects","policy:strict-execution","policy:zero-residue","provenance:agents-owned","role:governance","updates:manual","usage:on-demand"]'
  version: 2.0.0
---

# Safe Delete

Delete only exact, owned targets with an explicit recovery contract. This skill
also applies when an approved cutover supersedes tracked code: the replacement,
consumer rewire, and deletion are one atomic change, never a compatibility or
rollback sequence.

## Atomic source cutover

1. Resolve the superseded owner, replacement owner, every producer and consumer,
   tests, fixtures, config, generated surfaces, documentation, and semantic term.
2. Rewire every valid consumer to the final owner and delete the old tracked code
   in the same scoped patch. Git history is the recovery contract; do not archive,
   quarantine, copy, deprecate, alias, dual-read, or retain a rollback path.
3. Delete tests and artifacts that exist only for the old contract; rewrite tests
   for surviving behavior. A remaining valid consumer means the rewire continues,
   not that compatibility is preserved.
4. Prove zero residue, public runtime behavior, causal failure propagation, and
   native gates before the cutover can land.

## Artifact and data retirement

1. Resolve every literal target and classify it as declared generated output,
   tool-owned transient data, governed data, or unknown/concurrent work.
2. Inspect references, repository status, open handles or locks, special file
   types, and the canonical owner before mutation.
3. Preserve unknown, dirty, locked, live, database, symlink, and special-file
   content in place. Escalate the exact blocker; never infer ownership by name.
4. Remove generated output only through its declared cleanup primitive.
   A nonzero exit, timeout, signal, or incomplete cleanup propagates as the
   causal failure and leaves every later target untouched.
5. For approved untracked material that requires recovery, move the exact target
   atomically to the repository's declared same-filesystem quarantine or trash.
   If none exists, stop for an approved destination.
6. Verify the intended target is absent from the active surface, preserved items
   remain intact, the repository diff is scoped, and native gates are green.

## Rules

- Never use recursive broad deletion, unresolved variables or globs, `git clean`,
  destructive reset, global stash, or force deletion.
- Never stage backups, workspaces, repositories, databases, or reports in `/tmp`.
- Never create `.bak`/`.bkp` siblings that leave old and new implementations active.
- Never use artifact-retirement caution to retain superseded tracked code after an
  approved cutover; atomic rewiring and deletion are the safe operation.
- Never retry a failed deletion, substitute another command, or continue with a
  partial target set.
- Report what moved or was removed, its recovery location or irreversibility, and
  the exact validation evidence.
