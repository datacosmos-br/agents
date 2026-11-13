---
name: plan-reconciliation
description: "plan corpus reconciliation, attachment provenance, sequential integration"
license: MIT
metadata:
  aihub.tags: '["activation:opt-in","decision:ADR-0038","detect:opt-in:plan-reconciliation","effective:2026-11-03","extends:arch-docs","extends:beads","extends:doc-criteria","extends:focus-recovery","route:agent","subject:beads","usage:router"]'
---

# Plan reconciliation

Activate for an explicit request to reconcile a project's accumulated plans, their
attachments, implementation evidence and tracker links (`/reconcile-plans`); never for a
single document translation, a plan review without reconciliation or an isolated code
defect. Compose $doc-criteria for artifact selection, $arch-docs for decision evidence,
$beads (revalidation role) for tracker revalidation and $focus-recovery for interruption continuity,
from the same catalog.

An approved plan owns its topic: reconciling it adopts every correlated owner, WIP,
branch and PR by reviewed no-ff merge without destroying, stashing or reverting anything;
a diagnosis that ends in a verified-healthy service is complete, never a mandate to
reconfigure; and an operator-declared repository monopoly binds only the session the
operator names.

The outcomes are in [the procedure](references/procedure.md). Execution state lives only
in the selected Beads owner (`rules/workflow/beads-traceability.md`). Adapters,
destinations and the home projection come from the active configuration and AI Hub's
distribution owners, never from a new collector, projector or provider-home edit, and
neither this skill nor a historical plan grants Git or deployment authority.
