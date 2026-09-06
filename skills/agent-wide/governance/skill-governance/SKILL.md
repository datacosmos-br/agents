---
name: skill-governance
description: 'skill authoring, bundle governance, semantic evaluation'
license: MIT
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-08-29","policy:atomic-effects","policy:causal-subprocess","policy:fail-loud","policy:no-fallback","policy:preflight-before-effects","policy:strict-execution","policy:zero-residue","provenance:agents-owned","role:governance","updates:manual","usage:on-demand"]'
  version: 2.1.0
---

# Skill Governance

Activate when creating, changing, classifying, evaluating, or removing a skill
bundle. Read the `complete procedure` (skill file), search the active
catalog first, and create a new identity only for a distinct recurring
capability. Do not use this workflow for commands, agents, or rules.

Model specialization as an explicit `extends:<skill>` DAG. Load ancestors from
broadest to narrowest; each child references `$<parent>` and owns only its delta.
Never copy language, framework, library, or project detail into a broader skill.
