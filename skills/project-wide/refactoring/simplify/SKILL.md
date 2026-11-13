---
name: simplify
description: "simplest change, less code, deletion, diff size"
license: MIT
metadata:
  aihub.tags: '["decision:ADR-0038","effective:2026-11-03","usage:router"]'
  version: 3.0.0
---

# Simplify

The default pass for every change, applying laws 2 and 6 of `rules/law.md` to the paths
the change owns.

- Delete what the change leaves unused: dead branches, wrappers, conversions, restated
  defaults, duplicated expressions, comments that narrate code.
- Deleting internal code needs no proof beyond its missing consumer; `$yagni` covers
  data, other repositories and published contracts.
- Keep the public contract, each failure with its cause, and every effect.
- Shorter is not denser: no code golf, hidden control flow or single-caller helper.
- Report lines added and removed; a change that grew the code is redesigned before it
  lands.
