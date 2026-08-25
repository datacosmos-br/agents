---
name: skill-creator
description: "Author or fork a skill only after proving none exists. USE FOR: creating skills within the waza token budget, search-first reuse checks, scaffolding SKILL.md. DO NOT USE FOR: duplicating builtins or shared skills - compose those instead."
license: MIT
metadata:
  bundle: "governance"
  scope: "universal"
  version: "1.0.0"
---


# Skill Creator

Author a new skill only after proving one does not already exist. `config.AiHub.paths.agents_home` is
the universal skill authority; AI Hub distributes it. Keep every skill tiny and
project-fit, never a copy of a generic template.

## Use for

- Creating, building, or forking a skill for a real recurring workflow.

## Do not use for

- Duplicating an opencode builtin/shared skill (programming, ast-grep, debugging,
  refactor, review-work, git-master, ulw-research, explore) — compose it instead.

## Workflow

1. **Search first:** `ls {config.AiHub.paths.agents_home}/skills`, check builtins, `rg` the concept.
   If it exists, extend or compose — do not create.
2. **Scaffold** `{config.AiHub.paths.agents_home}/skills/<name>/SKILL.md` with frontmatter:
   `name`, `description` (start "Use when/for ...", name concrete triggers), and
   optional `license`/`metadata.version`.
3. **Body:** short sections — Use for / Do not use for / Workflow / Critical
   rules. Ground every instruction in this project's reality (Make verbs, facades,
   bd), not boilerplate.
4. **Budget:** SKILL.md must stay within `.waza.yaml` (≤500 tokens target).
   Validate: `ai-hub waza-check`.
5. **References:** put anything large in `references/*.md`, not SKILL.md.

## Critical rules

- One tight class of behavior per skill; no god-skills, no filler.
- Never author a skill that duplicates existing canonical behavior.
