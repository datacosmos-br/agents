---
description: Fan-out subagents for exploration/execution/validation; coordinator owns QA and publication
capsule_summary: |
  Universal law (operator ruling 2026-09-16): use the maximum of subagents to
  explore, execute, validate, and test in parallel; the main session keeps
  coordination, approval, final QA, and publication.
metadata:
  aihub.tags: '["decision:ADR-0021", "effective:2026-09-16", "route:both"]'
---

# Subagent fan-out with coordinator QA and publication (universal)

1. Parallelize with subagents: exploration (census, triage), execution
   (disjoint-file fixes), validation (gates, tests), and testing sweeps.
2. The main session coordinates, approves, performs final QA, and publishes.
3. Every subagent gets a bounded assignment, the standing rules, and reports
   evidence (commands, exits) back; the coordinator lands and publishes.
