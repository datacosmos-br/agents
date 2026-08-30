---
name: fix-forward-collaboration
description: 'concurrent work, integration adoption, anti-rollback coordination'
metadata:
  aihub.tags: '["decision:plan-00","effective:2026-08-29","policy:atomic-effects","policy:causal-subprocess","policy:fail-loud","policy:no-fallback","policy:preflight-before-effects","policy:strict-execution","policy:zero-residue","provenance:agents-owned","role:governance","updates:manual","usage:router"]'
---

# Fix-forward collaboration

When adopting an overlapping lane's PR work, inventory its unresolved review
threads and failing checks first with
`skills/tool/pr-sheriff/scripts/pr_triage.py` (pr-sheriff), and answer them
from the combined tree rather than from either lane's stale view.
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
