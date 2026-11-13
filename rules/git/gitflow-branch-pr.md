---
description: Publishing work — commit, push, pull request, merge and lane retirement.
metadata:
  aihub.tags: '["decision:ADR-0038","effective:2026-11-03","route:personal"]'
---

# Branch and pull request

Each repository declares its integration branch; promotion past it needs the operator.
Work continues in the authorized checkout, in a dedicated worktree when the project's
lane rules ask for one. A PR has one Git root. Only small, complete, green slices reach a
working branch or PR; unfinished work goes only to an authorized preservation ref, which
is not delivery. A moved base enters by `git merge --no-ff`; a lane lands as a merge
commit on its exact green head, with resolved review conversations and approval by
another actor, never with `--no-verify` or `[skip ci]`, and an administrative merge only
on the operator's explicit authorization. The merged revision is re-proven
([law](../law.md) 10). Local work, in any repository or subproject, is discarded only
once each real contribution in it is on the forge in an authorized preservation ref
referenced by a tracker item; a patch or local copy is not preservation. Its owner, or
the actor the operator authorized to adopt it, then deletes a lane, local and remote,
once a just-fetched base shows it holds nothing unique. A landed lane is retired the
same way in the same cycle; a primary or shared checkout and an integration branch are
never retired. Preservation and retirement run through the
operator's runtime tooling, which a consumer project never integrates or documents as
usage (tracker `operator-order-2026-11-05-preserve-on-forge`).
