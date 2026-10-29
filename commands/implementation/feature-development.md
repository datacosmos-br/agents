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

The approved specification is binding under
[operator precedence](../../rules/coordination/operator-precedence.md). Before any
deviation, present the exact difference, evidence, reason, impact and alternatives
and obtain the operator's explicit decision. Reducing code never reduces acceptance.
An approved requirement is supported by the specification; YAGNI never authorizes
dropping it.

When the input is an implementation plan, consume its approved `plan-review` result. A
blocker or unresolved material decision keeps implementation closed; do not silently
complete the plan while coding.

1. Read project instructions, architecture, public interfaces, existing owners,
   dependencies, consumers, runtime entry points, tests, and native gates.
2. Search for equivalent or reusable behavior. Apply YAGNI to remove unsupported scope,
   elect one SSOT, and change design boundaries only where the surviving requirement
   proves they are necessary.
3. Reconcile the owning ADRs, documentation, selected plan, tracker and canonical
   skills/rules/commands before code. For projection or deployment, resolve enabled
   capabilities, owned selectors and native formats from declarations; apply
   [atomic-effects](../../rules/runtime/atomic-effects.md) through the existing
   planner and publisher. Require a minimum per-target diff, preserved foreign
   content, authenticated withdrawal and a byte-identical no-op. Provider-specific
   decisions remain in the consuming project's policy.
   Reuse typed declaration collections and authenticated captures/parsed facts.
   Generated output must already conform; repair its producer rather than appending
   a post-generation fixer or editing a projection.
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
7. Record each delivery checkpoint through the selected available tracker under
   [Beads traceability](../../rules/workflow/beads-traceability.md): source revision,
   command, working directory, exit status, decisive output and next required proof.
   Keep source, integrated-revision and installed-runtime receipts distinct. Follow
   [Git integration](../../rules/git/gitflow-branch-pr.md) and
   [phase admission](../../rules/workflow/phase-admission-protocol.md) before closure;
   this invocation grants no publication, merge or activation authority by itself.

Return the accepted behavior, owner and reuse decision, consumers changed, runtime
proof, exact gate exits, and any blocker. Do not describe a partial, branch-only, or
unintegrated implementation as complete.
