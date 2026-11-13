---
name: dry
description: "semantic duplication, single owner, measured reduction, less code"
license: MIT
metadata:
  aihub.tags: '["decision:ADR-0038","effective:2026-11-03","usage:router"]'
  version: 2.0.0
---

# DRY

Each fact, rule and behavior has one owner; every copy is deleted and its consumers call
the owner (`rules/law.md` laws 2 and 3). Less code is the goal, and it is measured:
report the lines and the duplicates the project's detector finds, before and after, on
the same scope and configuration.

- Duplication is shared meaning or repeated work, not similar text: read both copies
  before merging them.
- Merge into the existing owner, never into a new utility bag, registry, framework or
  generated copy.
- A repeated value equal to its owner's default is a copy; consumers keep only real
  overrides.
