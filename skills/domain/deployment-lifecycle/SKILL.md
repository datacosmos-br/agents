---
name: deployment-lifecycle
description: 'project association, development lifecycle, immutable release, runtime deployment'
license: MIT
metadata:
  aihub.tags: '["activation:detected","decision:ADR-0008","detect:selected-tag:internal","detect:selected-tag:third-party-fork","domain:deployment","effective:2026-09-04","policy:atomic-effects","policy:fail-loud","policy:no-fallback","policy:strict-execution","provenance:agents-owned","route:project","updates:manual","usage:router"]'
---

# Deployment lifecycle

Resolve project profile, source identity, upstream identity when applicable,
integrated commit, manifest-owned runtime, build owner, deployment target, and
native acceptance command before effects. Development state and source checkout
execution are not deployment evidence.

Build one immutable artifact from the integrated commit, record its version and
digest, stage on the destination filesystem, exercise the native public surface,
activate atomically, and prove the installed artifact and configuration after
activation. A failure preserves the previous active state, remains red, and
leaves no partial candidate.

For `third_party_fork`, compose this procedure with `upstream-fork-maintenance`;
do not introduce local architecture, DI, typing, or language modernization.
