---
name: flext-development
description: 'flext framework, facade architecture, generated ownership, fleet development'
metadata:
  aihub.tags: '["activation:detected","decision:ADR-0008","detect:dependency:python:flext-core","detect:selected-tag:flext","effective:2026-08-29","extends:python-development","framework:flext","policy:atomic-effects","policy:causal-subprocess","policy:fail-loud","policy:no-fallback","policy:no-keyring","policy:preflight-before-effects","policy:required-environment","policy:strict-execution","policy:zero-residue","provenance:agents-owned","route:project","technology:python","updates:manual","usage:router"]'
---

# FLEXT development

Activate when project selection declares `flext` or a manifest depends on
`flext-core`, and the task changes FLEXT architecture, generation, packaging, or
fleet behavior. Do not activate for generic Python work without FLEXT evidence.
Activation also requires the `internal_flext` project profile. A third-party
fork follows upstream even when it exposes a FLEXT marker or dependency.

Compose `$python-development` first; it already composes `$solid`. This skill
contains only the FLEXT-specific architecture and fleet delta.

Read the `development procedure` (skill file). Resolve the active
repository's manifest, branch-matched owners, generated boundaries, dependency
graph, public consumers, and native Make gates before effects. Preserve the
canonical facade direction, typed boundary, single generated projection path,
and members-before-umbrella integration order.

Missing authority, an external source reference, a reverse runtime edge, a
hand-edited projection, or a broken canonical command fails before publication.
Fix the owning source forward, regenerate once, prove a fixed point, exercise the
real public runtime, and run every affected native gate.

The procedure owns the exact Python 3.13, Pydantic 2, facet, layer, and explicit
composition-root contract.
