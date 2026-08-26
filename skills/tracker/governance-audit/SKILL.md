---
name: governance-audit
description: Standing drift and staleness audit for the Beads tracker and canonical doc surfaces. Use for periodic hygiene checks (stale references, dead links, epic overlap, claim concentration, surface drift). Recommend-only; the orchestrator enacts semantic changes.
bundle: beads
scope: universal
---

# Governance Audit

## Authority

`{config.AiHub.paths.agents_home}/AGENTS.md` §Standing-Documenter, §Standing-Governance-CI,
§Reporting-And-Non-Stall; `UNIVERSAL_CORE.md` 1/11; `governance/rules`
§Role-Gate — not restated here. Standing duty, always active, outside the
five implementation lanes. You detect, document, recommend; the orchestrator
enacts, merges, closes. Doc fixes ship small and frequent through your own
bead/worktree/PR.

## Tracker Hygiene Checklist

1. `in_progress` AND dependency-blocked (state conflict).
2. Stale `blocked`; blocks on closed issues.
3. Epics with NULL descriptions; placeholder titles.
4. Claim concentration — risk report.
5. Zombie lanes: `in_progress` without a live worker.
6. Priority inflation: P0+P1 dwarfing P2.
7. Epic overlap → propose fold; ≥70% closed + ≤2 open → drain; bulk-touched `updated_at` → audit content, not dates.

Copy-paste recipes: [references/audit-recipes.md](references/audit-recipes.md).

## Content Staleness

- Dead references: `ls` every cited plan/ADR path; closed ancestor IDs cited as live context.
- Dual paths / source vs projection: authority = agents_home + project sources; tool homes are projections — audit diffs, regenerate, never edit projections.

## Report Format

Table: check | finding | evidence (command + decisive output) | proposed
action | severity (P0 dual-truth, P1 stale-block/NULL-epic/zombie, P2 rest).
To the orchestrator; reports never pause execution.

## Context Budget

Load: UNIVERSAL_CORE + this skill + AGENTS.md surface map. Skip:
worker/orchestrator playbooks — you recommend; they enact.
