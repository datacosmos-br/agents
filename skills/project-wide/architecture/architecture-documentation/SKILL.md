---
name: architecture-documentation
description: 'architecture decisions, system boundaries, technical documentation'
metadata:
  aihub.tags: '["decision:plan-00","effective:2026-08-29","policy:atomic-effects","policy:causal-subprocess","policy:fail-loud","policy:no-fallback","policy:preflight-before-effects","policy:strict-execution","policy:zero-residue","provenance:agents-owned","role:documentation","updates:manual","usage:on-demand"]'
---

# Architecture Documentation

Read `the evidence procedure` (skill file) before documenting system
structure, ownership, data flow, runtime topology, or an architectural decision.

Use maintained code, configuration, schemas, and runtime observations as the
source of truth. Invoke `documentation-criteria` for project-owned document and
ADR templates instead of duplicating them here. Never fabricate a component,
copy an owned contract into a second authority, or present a proposal as current
architecture.
