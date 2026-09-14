---
name: search-first
description: 'owner discovery, reusable code, architecture research'
license: MIT
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-08-29","usage:router"]'
  version: 1.2.0
---

# Search First

Research the active project before the first technical design or implementation
edit. Resolve the project contract, architecture, canonical owner, equivalent
code, pinned dependencies, current consumers, runtime, and native gates.

Apply automatically to features, fixes, refactors, integrations, dependency or
configuration changes, and new abstractions. Read the
`search and decision procedure` (skill file).

Produce one reusable evidence packet and follow the bounded owner route in the
procedure. That procedure is the SSOT for sequencing `yagni`, `ssot`, `solid`,
`simplify`, and conditional `dry`; do not duplicate the route here.

Do not activate for pure summarization, translation, formatting, or non-technical
questions. Do not rerun discovery while its owner, scope, dependency set, and
consumer evidence remain current. Missing or contradictory project evidence is a
loud blocker, never permission to invent architecture or duplicate code.
