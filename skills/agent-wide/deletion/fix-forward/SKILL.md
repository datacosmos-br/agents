---
name: fix-forward
description: 'concurrent work, integration adoption, anti-rollback coordination'
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-08-29","supersedes:skill:fix-forward-collaboration","usage:router"]'
---

# Fix-forward collaboration

When adopting an overlapping lane's PR work, inventory its unresolved review
threads and failing checks first with `pr-sheriff`, using AI Hub forge resolution
and direct GitHub evidence, and answer them from the combined tree rather than
from either lane's stale view.
Activate when work overlaps another agent or lane, integration has advanced, or
a rollback, stash, reset, revert, rebase, force-push, or whole-file replacement
is proposed.

Load the canonical invariant
`rules/coordination/fix-forward-collaboration.md` and follow the
`sync procedure` (skill file). Adopt the complete current authorized-
worktree state regardless of provenance or age, inventory owners and intent
before effects, preserve compatible work, integrate it forward through the
repository's declared lane, and revalidate the combined result. Use transaction
rollback only for effects created by the failing invocation.

If two evidenced current intentions cannot coexist under the active authority,
stop before the conflicting effect and ask the operator one exact question.
Never classify ordinary overlap, divergence, a failed gate, or required merge
work as a severe conflict.

Align a lane by integrating the declared integration branch with
`git merge --no-ff`. Rebase, force-push, cherry-pick replacement, and branch
rewriting are prohibited for authorized shared work — `git/gitflow-branch-pr`
(rule file) owns that law; they destroy the merge
history needed to prove which integration state was validated.
