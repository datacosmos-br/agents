---
name: python-refactoring
description: python, refactoring, analyzing, focused, opportunities
---

# python-refactoring

Use this skill to analyze Python code for refactoring opportunities.

## Checks

- Long functions (>30 lines) → extract smaller functions.
- Dead code → remove unreachable branches and unused imports.
- Type safety → avoid `Any`, add explicit types.
- Duplication → deduplicate repeated logic.

## Usage

Apply these checks manually or run project-specific tools (`vulture`, `refurb`, `rope`) via `make lint`.
