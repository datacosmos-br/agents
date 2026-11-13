---
name: feature-development
description:
  Implement one approved feature through project owners, consumers, runtime, and gates.
argument-hint: "<approved feature contract or specification>"
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-10-28","route:project"]'
---

# Feature development

Treat `$ARGUMENTS` as the approved feature contract. Refuse implementation when the
requested outcome, consumer, boundary, or acceptance behavior is genuinely ambiguous.

The approved specification is binding ([the law](../../rules/law.md)): any deviation,
including dropping an approved requirement, needs the operator's explicit decision, and
less code never means less acceptance.

When the input is an implementation plan, consume its approved `plan-review` result. A
blocker or unresolved material decision keeps implementation closed; do not silently
complete the plan while coding.

1. Read project instructions, architecture, public interfaces, existing owners,
   dependencies, consumers, runtime entry points, tests, and native gates.
2. Search for equivalent or reusable behavior. Apply YAGNI to remove unsupported scope,
   elect one SSOT, and change design boundaries only where the surviving requirement
   proves they are necessary.
3. Before code, correct the owning ADRs, documentation, selected plan, tracker and
   canonical skills, rules and commands the change would contradict. A projection or
   deployment goes through the existing planner and publisher: each effect is complete
   or absent, foreign content is kept and a second run changes nothing
   ([the law](../../rules/law.md) items 5 and 8). Provider-specific decisions stay in
   the consuming project's policy. Generated output conforms at its producer, never
   through a post-generation fixer or an edited projection.
4. Establish the expected public behavior from the approved contract and its real
   consumer. Reproduce the relevant current behavior before tests encode it; an
   observed defect never becomes the expected contract.
5. Implement through the selected owner, rewire current consumers and remove obsolete
   paths. Update tests, fixtures, examples and documentation to the final public
   interface. Generate production projections through their native owner, not pytest.
6. Exercise the public candidate and apply `$make-check` for the affected native
   format, lint, type, test, build, security, documentation and generation gates.
   Deadlines and test selection follow `rules/workflow/canonical-commands.md`.
   Respect an explicitly documentary scope; excluded implementation findings remain
   identified without an unauthorized repair or false completion.
7. Record each checkpoint with its evidence and next required proof in the selected
   tracker ([Beads traceability](../../rules/workflow/beads-traceability.md)) and close
   through [Git integration](../../rules/git/gitflow-branch-pr.md) and
   [the law](../../rules/law.md) item 10; this invocation grants no publication, merge
   or activation authority by itself.

Return the accepted behavior, owner and reuse decision, consumers changed, runtime
proof, exact gate exits, and any blocker. Do not describe a partial, branch-only, or
unintegrated implementation as complete.
