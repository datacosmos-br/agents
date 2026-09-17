---
description: Documentation follows runtime reality
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-08-25","route:both"]'
---

# Documentation follows runtime reality

Documentation is a maintained product surface, not historical proof by itself.
Before editing, identify each claim's runtime/config/schema/code owner and
whether the file is canonical, generated, historical, or proposed.

- Change canonical docs, skills, commands, rules, ADRs, executable examples,
  and public docstrings in the same grain as the behavior or decision.
- Preserve historical evidence as dated evidence; remove its authority to direct
  current execution. Never present a proposal, plan, or old gate result as live
  architecture.
- Change generated documentation only through its config/template/generator,
  regenerate it with the repository's canonical verb, and prove a second-run
  fixed point.
- Validate links, commands, snippets, schemas, and the real public consumer.
  Documentation gates and tests confirm that observation; they do not replace
  it.
- Remove extinct contracts and duplicate explanations. State purpose,
  ownership, interface, and observable contract rather than copied
  implementation or configurable values.

Compose with `runtime is reality`, `generators not projections`, and the
project's documentation-drift skill.
