---
name: governance-audit
description: "Standing drift and staleness audit for the Beads tracker and canonical doc surfaces. USE FOR: periodic hygiene checks (stale references, dead links, zombie lanes, claim concentration), recommending reconciliations to the orchestrator. DO NOT USE FOR: enacting semantic changes (beads-orchestrator); implementing beads (beads-worker)."
license: MIT
metadata:
  bundle: beads
  scope: universal
---

# Governance Audit

Standing duty, always active, outside the five implementation lanes. Detect, document, recommend; the orchestrator enacts, merges, closes. Authority: AGENTS.md §Standing-Documenter, CORE Laws 1/11, `governance/rules` §Role-Gate.

## Tracker hygiene checklist

1. `in_progress` AND dependency-blocked (state conflict).
2. Stale `blocked`; blocks on closed issues.
3. Epics with NULL descriptions; placeholder titles.
4. Claim concentration (one assignee holding the board) — risk report.
5. Zombie lanes: `gt agents` + `bd list --status in_progress` cross-check; stale hooks via `gt hook show`.
6. Priority inflation: P0+P1 dwarfing P2.
7. Epic overlap on one directive → propose fold; ≥70% closed + ≤2 open → drain.

Copy-paste recipes: [references/audit-recipes.md](references/audit-recipes.md).

## Content staleness

- Dead references: `ls` every cited plan/ADR path; closed ancestors cited as live context.
- Dual paths: same artifact in two locations — record the live one, propose reconciliation.
- Source vs projection: config sources are authority; tool homes are projections — audit diffs, regenerate from source, never edit projections.

## Report format

Table: check | finding | evidence (command+output) | proposed action | severity (P0 dual-truth, P1 stale-block/NULL-epic/zombie, P2 rest). To the orchestrator; reports never pause execution. Activity context via `gt trail`, `gt audit <actor>`.

## Context budget

Load: CORE + this skill + AGENTS.md surface map. Skip worker/orchestrator playbooks — you recommend; they enact.
