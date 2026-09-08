---
name: governance-audit
description: 'governance drift, authority conflicts, stale instructions'
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-08-29","usage:on-demand"]'
---

# Governance Audit

Resolve the active project instructions, tracker owner, canonical documents,
projection owner, and runtime state before auditing. You detect, document, and
recommend; the declared owner enacts, merges, and closes. During tracker
suspension, inspect only supplied static snapshots and repository files.

Read the `audit recipes` (skill file) for the single classification
and severity contract. Inspect content, ownership, dependencies, live work, and
source/projection bytes; timestamps alone do not establish staleness.

Return one table of check, finding, decisive evidence, owner-correct action, and
severity. A blocking finding or failed read-only inspection stops at its first
cause. Do not mutate the tracker or a projection, invoke suspended tooling, load
worker/orchestrator playbooks without that role, or continue after failed
preflight.
