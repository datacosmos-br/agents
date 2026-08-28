---
name: gascity-change-lifecycle
description: 'gas city, change lifecycle, runtime orchestration'
metadata:
  aihub.tags: '["activation:opt-in","detect:opt-in:gascity","provenance:agents-owned","route:agent","tool:gascity","updates:manual","usage:on-demand"]'
---

# Gas City Change Lifecycle

Use for landing a project change coordinated by Gas City. Gas City owns
dispatch and observation; the repository owns Git, gates, review, and merge.

## Workflow

1. Resolve the declared city, rig, agent, formula, and work identifier.
2. Dispatch only through a configured formula and observe the resulting run.
3. Use the repository's native branch, commit, push, and PR contracts.
4. Merge into the configured integration branch and validate the merged SHA.
5. Close the work only after integration evidence exists.

## Critical rules

- `gc sling <agent> <work> --on <formula>` is dispatch, not Git landing.
- No `gc commit`, `gc done`, implicit Refinery, rebase, or force-push.
- Do not run Gas City while runtime is explicitly suspended.
- Read the repository owner document `rules/gascity.md`; do not duplicate it.
