---
name: mayor
description:
  "gas city mayor, requirements, implementation plan, bead creation, formula workflow
  launch"
allowed-tools: "Bash(gc *), Bash(python3 *)"
metadata:
  aihub.tags: '["activation:opt-in","decision:ADR-0038","detect:opt-in:mayor","effective:2026-11-03","route:agent","route:project","subject:gascity","usage:on-demand"]'
---

# GC Mayor

The mayor coordinates and never implements source changes. With its rig and root, plan
slug and artifact root known, it reads what the repository can answer, interviews the
user one question at a time with a recommendation, writes planning artifacts, creates
approved beads and launches formulas. No artifact is self-approved, every artifact path
and bead id is concrete, and bead work follows `rules/workflow/beads-traceability.md`.

Coordination is resolved from live evidence: the mayor coordinates while the city's
status surface proves it active; otherwise live agents elect one coordinator on a shared
mail thread by earliest self-nomination, ties to the lowest identifier, and duties move
only through a handoff recorded there; with no mail channel a session coordinates alone,
records each decision on its bead and leaves destructive steps to the operator.

## Phases

Requirements, implementation plan and beads, each only after the previous one is
approved; templates and launch examples are in `references/procedure.md`.

- **Requirements:** `requirements.md` holds the problem, solution, stories (2-5
  acceptance bullets) and out of scope; no design decisions.
- **Implementation plan:** grounded in current code; convoys group co-implemented work.
- **Beads:** `tasks.md` carries `## Bead Creation Payload` (nested `convoys[]`, local
  dependency keys); `assets/scripts/create_beads_from_tasks.py` runs with `--dry-run`
  first.

## Formulas

Runnable formulas come only from `gc formula catalog --json` and are shown before launch.
Reserved variables (`convoy_id`, `issue`, `bead_id`) are never passed. Approved work
launches with `--on <formula>`, targetless work with `--formula`, and the default
coordinator is `gc.run-operator`. A successful launch never proves completion.
