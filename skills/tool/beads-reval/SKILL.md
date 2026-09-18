---
name: beads-reval
description: "beads revalidation, open issues, closed issues, integrated code evidence"
metadata:
  aihub.tags: '["activation:opt-in","decision:ADR-0008","detect:opt-in:beads-reval","effective:2026-09-14","route:agent","subject:beads","usage:router"]'
---

# Beads revalidation

Use for an explicitly requested revalidation of registered issues, including closed
issues. Do not activate for an unrelated implementation or translation.

Read [the procedure](references/procedure.md) completely before changing tracker state.
Follow the existing coordination/beads-verification and coordination/plan-topic-monopoly
rules for evidence and the active intent.

Beads owns execution state and the resumption cursor. Exported inventories are read-only
evidence, never a second status ledger. Use only the selected available tracker;
suspension does not authorize a substitute.

Revalidation is semantic: a stale closed issue may require correction, while an open
issue may already be implemented or superseded. Neither status nor text similarity
establishes reality. Preserve unique evidence before consolidation.
