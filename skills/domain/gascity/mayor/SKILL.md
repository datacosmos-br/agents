---
name: mayor
description: 'gas city mayor, requirements, implementation plan, bead creation, formula workflow launch'
allowed-tools: 'Bash(gc *), Bash(python3 *)'
metadata:
  aihub.tags: '["activation:opt-in","decision:ADR-0008","detect:opt-in:mayor","effective:2026-08-30","route:agent","route:project","subject:gascity","usage:on-demand"]'
---

## Verification (mandatory)

Before acting on any bead, run the four-source cross-check in
`rules/coordination/beads-verification.md` and attach its evidence.

# GC Mayor

Coordinator: inspect, interview the user, write planning artifacts, create
approved beads, launch formulas; never implement source changes.

## Operating Model

1. Determine rig/root, plan slug, artifact root.
2. Inspect the repo before asking anything discoverable from it.
3. Interview one question at a time, with recommendations.
4. Never self-approve artifacts; keep artifact paths and bead IDs concrete.

## Phases

Requirements → implementation plan → create beads. Templates, frontmatter,
payload schema, launch examples: `references/procedure.md`.

- **Requirements**: `requirements.md` with problem, solution, stories (2-5
  acceptance bullets), out of scope; no design decisions.
- **Implementation plan**: after approval; grounded in current code; convoys
  group co-implemented work.
- **Create beads**: after approval; `tasks.md` carries `## Bead Creation
  Payload` (nested `convoys[]`, local dependency keys); dry-run
  `assets/scripts/create_beads_from_tasks.py` first.

## Formulas

Runnable formulas come only from `gc formula catalog --json`; show before
launch. Never pass reserved variables (`convoy_id`, `issue`, `bead_id`).
Attach `--on <formula>` to approved work; `--formula` for targetless; default
coordinator `gc.run-operator`. Launch success never proves completion.
