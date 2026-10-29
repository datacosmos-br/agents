---
description: Documentation follows runtime reality
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-10-25","route:both"]'
---

# Documentation follows runtime reality

Documentation is a maintained product surface, not historical proof by itself. Before
editing, identify each claim's runtime/config/schema/code owner and whether the file is
canonical, generated, historical, or proposed.

The documentation-first sequence and fork boundary belong to
`rules/architecture/engineering-core.md`. Establish that documented alignment before
implementation, then apply this surface-maintenance contract while adopting concurrent
work through the fix-forward rule, never requiring a globally stable checkout.

- Consult and reconcile affected guides, README, AGENTS, ADRs, selected tracker
  references, approved plans, local skills, rules, commands and propagated
  skill/source identities before code changes.
   Change canonical docs, plans, skills, commands, rules, executable examples and public
   docstrings in the same grain as the behavior or decision, through their owners.
   Repeat this consultation at phase transitions, context recovery and new operator
   decisions; keep the affected sources aligned throughout execution, not just at intake.
- Preserve historical evidence as dated evidence; remove its authority to direct current
  execution. Never present a proposal, plan, or old gate result as live architecture.
- Keep each delivery's source, integration and installed-runtime claims linked to
  their distinct receipts through [Beads traceability](beads-traceability.md) and
  [phase admission](phase-admission-protocol.md). Documentation alignment never
  supplies missing execution evidence or publication authority. Project-specific
  recovery authorization remains in that project's owner, not in universal rules.
- Change generated documentation only through its config/template/generator, regenerate
  it with the repository's canonical verb, and prove a second-run fixed point.
- Validate links, commands, snippets, schemas, and the real public consumer.
  Code in docstrings and Markdown receives the project's source formatting, lint,
  type, rule and execution gates through their native owners; keep examples current.
  Documentation gates and tests confirm that observation; they do not replace it.
  Test changes follow implemented real behavior under `runtime-is-reality`; an atomic
  cutover never permits reversing that internal order.
- Remove extinct contracts and duplicate explanations. State purpose, ownership,
  interface, and observable contract rather than copied implementation or configurable
  values.

Compose with `runtime is reality`, `generators not projections`, and the project's
documentation-drift skill.
