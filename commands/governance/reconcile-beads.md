---
name: reconcile-beads
description: Reconcile a Beads backlog from integration evidence in bounded, reviewed cycles.
argument-hint: "--limit N --integration REF [--beads ID,...]... [--output FILE.csv | --dry-run]"
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-09-10","route:project"]'
---

# Reconcile Beads

Treat `$ARGUMENTS` as bounds, exact bead IDs, and an optional CSV path. Load the
`beads-organization` skill. Resolve tracker authority and Gas City state before
effects. A suspended tracker remains read-only unless the current operator
explicitly authorizes mutations to that exact store.

1. Run the skill inventory script with explicit `--limit` and `--integration`;
   pass repeated or comma-separated `--beads` when supplied. Use `--limit 0`
   only for an explicit complete sweep. Dry-run writes CSV only to stdout.
2. Correlate each row with registered state, integration Git history, measured
   reality, and current integrated code. Include plans, session exports, docs,
   ADRs, worktrees, and GitHub PRs as evidence, never authority by age alone.
3. Treat the CSV as an unreviewed queue, never write authorization. Apply only
   changes explicitly represented as reviewed input with current evidence, and
   re-read each selected bead first. Preserve published SHAs. Release claims and
   change deferred state only with current evidence.
4. Stop each write batch at 20 operations. Record its IDs and evidence on the
   coordinator bead. Validate duplicates, cycles, graph state, and conventions.
5. Sync only a validated batch. Record the exact sync result. Restart from a
   fresh inventory until the requested population has zero unadjudicated rows.
