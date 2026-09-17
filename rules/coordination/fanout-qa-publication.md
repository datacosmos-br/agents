---
description: Fan-out subagents for exploration/execution/validation; coordinator owns QA and publication
capsule_summary: |
  Universal law (operator ruling 2026-09-16): use the maximum of subagents to
  explore, execute, validate, and test in parallel; the main session keeps
  coordination, approval, final QA, and publication.
metadata:
  aihub.tags: '["decision:ADR-0021", "effective:2026-09-16", "route:both"]'
---

# Maximize safe fan-out; keep one publication owner

The `parallel delegation` rule owns assignment boundaries, cost routing,
evidence review, and sequenced effects. Within that contract, use the maximum
useful fan-out for disjoint exploration, edits, and validation. The coordinator
alone adjudicates overlaps, runs final QA, updates tracker state, and publishes.
