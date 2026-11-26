---
description: Publishing work — commit, push, pull request, merge and lane retirement.
metadata:
  aihub.tags: '["decision:ADR-0038","effective:2026-11-03","route:personal"]'
---

# Branch and pull request

Each repository declares its integration branch; promotion past it needs the operator.
Work continues in the authorized checkout, in a dedicated worktree when the project's
lane rules ask for one. A PR has one Git root and carries one complete work step.
When the operator authorizes aggregation, combine related local branches into one
complete work step, one PR and one exact-head integration CI per repository.
Unfinished work goes only to an authorized preservation ref. A moved base enters by
`git merge --no-ff`; the project's declared integration actor lands a lane on
its exact green head, in the method its branch class declares, once the declared checks
pass and review conversations are resolved, never with `--no-verify` or `[skip ci]`; an
administrative merge is the operator's own act, never an agent's. The merged revision
is re-proven ([law](../law.md) 10). Local work, in any repository or subproject, is discarded only
once each real contribution in it is on the forge in an authorized preservation ref
referenced by a tracker item; a patch or local copy is not preservation. Its owner, or
the actor the operator authorized to adopt it, then deletes a lane, local and remote,
once a just-fetched base shows it holds nothing unique. A landed lane is retired the
same way in the same cycle; a primary or shared checkout and an integration branch are
never retired. Preservation and retirement run through the
operator's runtime tooling, which a consumer project never integrates or documents as
usage (tracker `operator-order-2026-11-05-preserve-on-forge`).

A pull request needs the native hook and exact-head CI evidence defined by
[canonical commands](../workflow/canonical-commands.md) and the real entry point proof
in [law 9](../law.md). Integration CI runs the project's test verb; a CI that omits it
is a defect at its CI owner (`operator-order-2026-11-21-done-no-excuses`). Integrate the step before the same actor opens the next one
(`operator-order-2026-11-15-pr-is-one-validated-step`). At the end of every plan phase
and of the plan, each green PR is merged into the integration branch with a merge
commit, and a red one is fixed forward before the next phase starts
(`operator-order-2026-11-21-integration-pr-every-phase`).
