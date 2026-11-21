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
is not delivery. A moved base enters by `git merge --no-ff`; a lane lands by the forge's automatic merge on
its exact green head, in the method its branch class declares, once the declared checks
pass and review conversations are resolved, never with `--no-verify` or `[skip ci]`; an
administrative merge is the operator's own act, never an agent's (tracker
`operator-order-2026-11-15-pr-queue-and-auto-merge`). The merged revision is re-proven
([law](../law.md) 10). Local work, in any repository or subproject, is discarded only
once each real contribution in it is on the forge in an authorized preservation ref
referenced by a tracker item; a patch or local copy is not preservation. Its owner, or
the actor the operator authorized to adopt it, then deletes a lane, local and remote,
once a just-fetched base shows it holds nothing unique. A landed lane is retired the
same way in the same cycle; a primary or shared checkout and an integration branch are
never retired. Preservation and retirement run through the
operator's runtime tooling, which a consumer project never integrates or documents as
usage (tracker `operator-order-2026-11-05-preserve-on-forge`).

A pull request is one complete work step, proven at the real entry point and gated by
its hooks and integration CI in the delivery sequence of
`rules/workflow/canonical-commands.md`; it is integrated before the same actor opens the
next one (tracker memory `operator-order-2026-11-15-pr-is-one-validated-step`).
