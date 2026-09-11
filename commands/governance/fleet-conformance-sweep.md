---
name: fleet-conformance-sweep
description: Run the FLEXT trio/fleet conformance sweep using the frozen-ruler phases; records ruler, discovers, gates decisions, lands per-repo with runtime proofs.
argument-hint: "[optional repo-filter, e.g. charts|gitops|root]"
metadata:
  aihub.tags: '["effective:2026-09-11","route:project"]'
---

# Fleet conformance sweep (plan v5 execution recipe)

Companion to `docs/ARCHITECTURE/FLEXT_TRIO_CONFORMANCE_SWEEP_PLAN.md`
(plan bead `cosmos-3flk9`). Follow authority order, then phases:

## G0 — freeze the ruler (always first)
Pick ONE owner validator SHA (branch tip) and one configuration. Record in
the plan bead the tuple: validator repo+SHA, scan config (`scan_dirs`,
thresholds, strict modes), and every target repo+SHA. All counts in this
sweep refer to this ruler only; re-freeze when the owner tip moves.

## G1 — discovery (read-only, start immediately)
1. `class_prefix`/`proto_not_runtime`/`NS-STRUCT` violations → per-class
   consumer/cost tables (ast-grep). Output to the epic, not your session.
2. Facade contract audit: `api.py` class vs stem, nested MRO base count,
   ENFORCE-047/049 base order violations with exact classes.
3. Test-vs-runtime contract drift: for every pyrefly `missing-attribute` on
   fleet facades, verdict per call site (rename test vs dead API).

## G2 — decision gate
Present A(internal-only) / B(big-bang rename) / C(mixed) WITH the costed
tables. Only consumer-facing mutation waits here.

## G3 — owner lawship
Fix rule ambiguity at the validator owner and republish; do not burn 1,300
renames on an over-strict rule.

## G4 — per-repo conformance (dependency order)
`flext-core → flext-cli → flext-tests → flext-infra → charts → gitops →
root`. Per repo: hermetic deps (`env -u VIRTUAL_ENV -u
UV_PROJECT_ENVIRONMENT`), pinned lock + cooldown, `gen×2` fixed point,
`check`+`test APPLY=Y`, scoped commit → **PR** (no develop bypass), merge,
gates on merged SHA.

## G5 — runtime truth before any completion claim
Clean-venv CLI smoke per package; gitops source scan dry-run against a real
tenant reconciled with live Argo CD; `helm template` drift-check per chart.

## Hygiene gates
`make test` with 0 items selected is RED (no-tests-ran law); duplication
gate thresholds declared fail-closed; member venv must import
`flext_cli` after fresh `uv sync` from the committed lock.

Record evidence (command, cwd, exit code, decisive output) per step in the
plan bead; close only with 4-source evidence.
