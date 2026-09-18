---
name: fleet-conformance-sweep
description:
  Run the FLEXT trio/fleet conformance sweep using the frozen-ruler phases; records
  ruler, discovers, gates decisions, lands per-repo with runtime proofs.
argument-hint: "[optional repo-filter, e.g. charts|gitops|root]"
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-09-11","route:project"]'
---

# Fleet conformance sweep (plan v5 execution recipe)

Companion to `docs/ARCHITECTURE/FLEXT_TRIO_CONFORMANCE_SWEEP_PLAN.md` (plan bead
`cosmos-3flk9`). Follow authority order, then phases:

## G0 — freeze the ruler (always first)

Pick ONE owner validator SHA (branch tip) and one configuration. Record in the plan bead
the tuple: validator repo+SHA, scan config (`scan_dirs`, thresholds, strict modes), and
every target repo+SHA. All counts in this sweep refer to this ruler only; re-freeze when
the owner tip moves.

## G1 — discovery (read-only, start immediately)

Automation surface order (research 2026-09-11):

1. **Graph refresh first** (`rules/workflow/graph-truth-freshness.md`, operated per the
   `crg` skill freshness gate): `code-review-graph status --json --repo <root>` →
   `update --brief` (or `build` when update exits 1 or after rewrites) — never reason
   from a graph whose built commit differs from the target HEAD.
2. **Facade census at the owner tooling** (cheaper and stricter than grep):
   `flext-infra refactor census --repository-root <repo> --output-format json` and
   `flext-infra refactor namespace-enforce --repository-root <repo> --namespace c|m|p|u ...`
   produce the D1/D2 consumer and composition tables directly from Rope — use them as
   the authoritative inventory; ast-grep is the _pattern-level_ complement, not the
   owner of this data.
3. **ast-grep for fossil patterns** (branch-agnostic): global rules live in
   `~/agents/ast-grep-rules/universal`; per-project rules are generator output
   (`sgconfig.yml` ← `config/codegen.yaml`, `make gen` refreshes). Ad-hoc scans:
   `ast-grep scan --rule <file> <path>`; new recurring lint goes to the project rule dir
   via the generator SSOT, never a hand edit.
4. **`make mod`** (`flext-infra refactor mod --apply`) executes approved ast-grep rule
   rewrites at the declared scope — always the dispatcher, never direct ast-grep, so
   LSP/Rope telemetry stays consistent.
5. **CRG decision tables** (limits per the `crg` skill):
   `code-review-graph dead-code --json` (dead Protocol candidates for D4, confirmed in
   source), `impact --files <changed> [--base <sha>]` (rename blast radius for the F4
   cost table), `refactor suggest` (rename candidates). Read-only verbs only during
   discovery; renames land through G4 discipline.

Continue with D1–D4 as before, now equipped: D1 charts consumer inventory (census +
impact), D2 gitops facade inventory (namespace-enforce + query), D3 helper contract
audit (search + tests diff), D4 proto census (dead-code).

## G2 — decision gate

Present A(internal-only) / B(big-bang rename) / C(mixed) WITH the costed tables. Only
consumer-facing mutation waits here.

## G3 — owner lawship

Fix rule ambiguity at the validator owner and republish; do not burn 1,300 renames on an
over-strict rule.

## G4 — per-repo conformance (dependency order)

`flext-core → flext-cli → flext-tests → flext-infra → charts → gitops → root`. Per repo:
hermetic deps (`env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT`), pinned lock + cooldown,
`gen×2` fixed point, `check`+`test`, scoped commit → **PR** (no develop bypass), merge,
gates on merged SHA.

## G5 — runtime truth before any completion claim

Clean-venv CLI smoke per package; gitops source scan dry-run against a real tenant
reconciled with live Argo CD; `helm template` drift-check per chart.

## Hygiene gates

`make test` with 0 items selected is RED (no-tests-ran law); duplication gate thresholds
declared fail-closed; member venv must import `flext_cli` after fresh `uv sync` from the
committed lock.

Record evidence (command, cwd, exit code, decisive output) per step in the plan bead;
close only with 4-source evidence.
