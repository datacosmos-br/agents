---
description: Documentation follows runtime reality
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-11-02","route:both"]'
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
- Every adjustment converges everything it touches: code, Markdown documents, rules,
  tracker records and ADRs, in every project, in the same change (operator order
  2026-11-02, tracker memory `operator-order-2026-11-02-everything-converges`, verbatim
  excerpt: "os ajsutes tem que ser feitos em tudo, código, docuemtnos md, rules, beads,
  TUDO, em todos os projetos, sempre, nunca em pedeças quebrados que quebra o resto, nao
  podemos ter contradicoes, conflitos entre os docuemntos e sources e entre eles, tudo
  tem que convergir"). No contradiction or conflict may remain between documents and
  sources or among documents, and a fix never lands as a broken piece. A document that
  is a projection converges by editing its source and regenerating every projection,
  never by editing the copy. Ethics duty: `rules/ethics/professional-integrity.md`.
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
