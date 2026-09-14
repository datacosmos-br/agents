---
name: plan-reconciliation
description: 'plan corpus reconciliation, attachment provenance, sequential integration'
license: MIT
metadata:
  aihub.tags: '["activation:opt-in","decision:ADR-0008","detect:opt-in:plan-reconciliation","effective:2026-09-14","extends:arch-docs","extends:beads-reval","extends:doc-criteria","extends:focus-recovery","route:agent","subject:beads","usage:router"]'
---

# Plan reconciliation

Activate for an explicit request to reconcile a project's accumulated plans,
their attachments, implementation evidence, and tracker links. Do not activate
for a single document translation, a plan review without reconciliation, or an
isolated code defect. The command `/reconcile-plans` selects this workflow.

Compose $doc-criteria for artifact selection, $arch-docs for decision evidence,
$beads-reval for tracker revalidation, and $focus-recovery for interruption
continuity. Load those parents from the same catalog; do not copy their law.

Read [the procedure](references/procedure.md) and
[the source contract](references/input-contract.md) completely before effects.
Resolve source adapters, repository destinations, the home projection, project
dependencies, and integration lanes from the active configuration. Provider
exports are collected by the configured automation, not a manual prerequisite.

Use automated inventories as evidence, never as semantic decisions. Read the
active plan and all linked material completely. Reconcile one plan at a time,
newest first, and its projects in dependency order; retain the same plan through
its integration proof. Execution state lives only in the selected Beads owner.
Publish through the configured document and AI Hub distribution owners, never
through a new projector or provider-home edit.
