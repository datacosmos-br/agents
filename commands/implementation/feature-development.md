---
name: feature-development
description:
  Implement one approved feature through project owners, consumers, runtime, and gates.
argument-hint: "<approved feature contract or specification>"
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-08-29","route:project"]'
---

# Feature development

Treat `$ARGUMENTS` as the approved feature contract. Refuse implementation when the
requested outcome, consumer, boundary, or acceptance behavior is genuinely ambiguous.

When the input is an implementation plan, consume its approved `plan-review` result. A
blocker or unresolved material decision keeps implementation closed; do not silently
complete the plan while coding.

1. Read project instructions, architecture, public interfaces, existing owners,
   dependencies, consumers, runtime entry points, tests, and native gates.
2. Search for equivalent or reusable behavior. Apply YAGNI to remove unsupported scope,
   elect one SSOT, and change design boundaries only where the surviving requirement
   proves they are necessary.
3. Establish the expected public behavior from the approved contract and its real
   consumer. Reproduce the relevant current behavior before tests encode it; an
   observed defect never becomes the expected contract.
4. Implement through the selected owner, rewire current consumers and remove obsolete
   paths. Update tests, fixtures, examples and documentation to the final public
   interface. Generate production projections through their native owner, not pytest.
5. Exercise the public candidate and apply `$make-check` for the affected native
   format, lint, type, test, build, security, documentation and generation gates.
   Deadlines and test selection follow `rules/workflow/canonical-commands.md`.
   Respect an explicitly documentary scope; excluded implementation findings remain
   identified without an unauthorized repair or false completion.

Return the accepted behavior, owner and reuse decision, consumers changed, runtime
proof, exact gate exits, and any blocker. Do not describe a partial, branch-only, or
unintegrated implementation as complete.
