---
name: reconcile-plans
description:
  Reconcile the configured plan corpus sequentially through its integration boundary.
argument-hint: "[project or workspace]"
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-09-14","route:agent"]'
---

# Reconcile plans

Use $plan-reconciliation for the project or workspace named in `$ARGUMENTS`. With no
argument, use the current workspace only when its configured identity is unambiguous.
Resolve collection adapters, versioned documents, home projection, tracker, and
integration owners from configuration.

Collect sources automatically through their declared owner. Read the selected plan and
all attachments completely, reconcile current evidence and all related open/closed
Beads, update its documentation and ADR owners, then carry that one plan through
integration before selecting another. The command has no separate status ledger,
provider exporter, or projection implementation.
