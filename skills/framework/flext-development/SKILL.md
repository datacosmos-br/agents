---
name: flext-development
description:
  "flext framework, facade architecture, generated ownership, fleet development"
metadata:
  aihub.tags: '["activation:detected","decision:ADR-0008","detect:dependency:python:flext-core","detect:selected-tag:flext","effective:2026-08-29","extends:py-dev","route:project","subject:flext","subject:python","usage:router"]'
---

# FLEXT development

Activate when project selection declares `flext` or a manifest depends on `flext-core`,
and the task changes FLEXT architecture, generation, packaging, or fleet behavior. Do
not activate for generic Python work without FLEXT evidence. Activation also requires
the `internal_flext` project profile. A third-party fork follows upstream even when it
exposes a FLEXT marker or dependency.

Compose `$py-dev` first; it already composes `$solid`. This skill contains only the
FLEXT-specific architecture and fleet delta.

Read the `development procedure` (skill file). Resolve the active repository's manifest,
branch-matched owners, generated boundaries, dependency graph, public consumers, and
native Make gates before effects. Preserve the canonical facade direction, typed
boundary, single generated projection path, and members-before-umbrella integration
order.

Missing authority, an external source reference, a reverse runtime edge, a hand-edited
projection, or a broken canonical command fails before publication. Fix the owning
source forward, regenerate once, prove a fixed point, exercise the real public runtime,
and run every affected native gate.

The procedure owns the exact Python 3.13, Pydantic 2, facet, layer, and explicit
composition-root contract.

## Landing law delta (evidence 2026-09-11, plan `docs/plans/2026-09-11-flext-conformance-sweep.md`)

- "Go to the end" under operator pressure NEVER licenses skipping the landing flow: bead
  -> scoped mutation -> native gates -> lane branch -> PR -> review -> `--no-ff` merge
  -> gates rerun on the merged SHA. Direct fast-forward push to an integration branch is
  a recorded governance violation, not a speedup.
- Never discard (reset/rewrite) public history without a bead that inventories every
  hunk first; re-derive lost SSOT surgery hunk-by-hunk before declaring the discard
  complete.
- Pre-push guard for generated surfaces: `make gen && make gen` must produce
  byte-identical trees; only push on doubled idempotency. A fixed-point failure is a P0
  product defect (scaffolder SLA), never "out of scope" cleanup residue. Owner of this
  contract: ADR-010 §Verification contract (item 1, byte-idempotent ×2); this skill
  restates it for the pressure case, it does not re-invent it.
- After any mutation that touches the CI surface (Makefile.j2, workflow templates,
  pre-commit), re-run `pre-commit run --all-files` once to prove hook liveness against
  the regenerated tokens.
