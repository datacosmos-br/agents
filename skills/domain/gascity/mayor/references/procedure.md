# Mayor procedure — artifact templates and launches

## Shared frontmatter shape

Every artifact starts with YAML frontmatter; `phase` names the stage, `status` starts at
`draft`, and upstream files link each other:

```yaml
---
plan_slug: example-slug
phase: requirements # requirements | implementation-plan | tasks
rig: backend
rig_root: /absolute/path/to/rig
artifact_root: /absolute/path/to/rig/plans
requirements_file: /absolute/path/to/requirements.md # phase 2+
implementation_plan_file: /absolute/path/to/implementation-plan.md # phase 3
status: draft
created_at: 2026-05-10T00:00:00Z
updated_at: 2026-05-10T00:00:00Z
---
```

## requirements.md body

```markdown
# Requirements: <title>

## Problem Statement

## Solution

## User Stories

## Out Of Scope

## Other Notes
```

Capture constraints discovered from the repo. Do not preselect bead IDs or formula
targets in requirements.

## implementation-plan.md body

```markdown
# Implementation Plan: <title>

## Summary

## Current System

## Proposed Implementation

## Testing

## Rollout

## Open Questions
```

Be concrete for bead creation: name files/modules, interfaces, data flow, persistence,
error handling, migration concerns, and verification strategy where relevant.

## tasks.md and bead creation

`tasks.md` uses the tasks-phase frontmatter, a human-readable task plan, and a
machine-readable payload under `## Bead Creation Payload`. Use nested `convoys[]` for
arbitrary groupings (never `epics[]`); dependencies use local keys the script resolves
to bead IDs. Dry-run first; pass `--city /path/to/city` only when the city is not
discoverable:

```bash
python3 assets/scripts/create_beads_from_tasks.py --dry-run < artifact-root > / < plan-slug > /tasks.md
python3 assets/scripts/create_beads_from_tasks.py < artifact-root > / < plan-slug > /tasks.md
```

## Worked launches

```bash
gc sling gc.run-operator implement \
  --var artifact_root= \
  --var context_path= \
  --var drain_policy=separate < implementation-convoy-id > --on < artifact-root > / < plan-slug > /build < artifact-root > / < plan-slug > /context.yaml

gc sling gc.run-operator github-pr-review --formula \
  --var github_pr_url=https://github.com/ \
  post_mode=human_gate < owner > / < repo > /pull/ < number > --var
```
