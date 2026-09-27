---
name: mcb-handoff
description:
  "Produce or validate a marlonsc/mcb session handoff that only routes to durable
  sources (beads, ADR, runbook, rules, plans)."
argument-hint: "[--validate FILE | --bead ID]"
metadata:
  aihub.tags: '["decision:ADR-0021","effective:2026-09-27","route:project"]'
---

# mcb handoff

Treat `$ARGUMENTS` as either `--validate <file>` (check an existing handoff pointer)
or `--bead <id>` (write the handoff set for that bead's session). The product is a
pointer document, never a content duplicate: every subject names its durable source.

1. **Durable sources to fill or verify**:
   - bead description = the playbook (exact next command, remaining steps, quirks);
     comments = the full trail;
   - repo ADR `docs/adr/059-mimosa-advisory-triage-policy.md` for advisory triage
     rules D1–D5;
   - repo runbook `docs/developer/AGENT-OPERATIONS.md` for the battery, landing
     recipe, and quirks;
   - fleet rules `rules/coordination/mcb-session-operating-rules.md` and
     `rules/coordination/mimosa-advisory-triage.md` in the agents law repository;
   - cycle record with self-critique under `~/.claude/plans/<date>-<topic>-handoff/`.
2. **Pointer rules**: a handoff file stays under one screen, lists source paths in a
   table, and carries a one-line state summary. Any content block longer than a
   paragraph belongs in a source, not in the pointer.
3. **Validation**: every referenced path must exist and every bead id must resolve in
   the tracker; an in-flight lane must have its uncommitted state described as
   correct-and-kept (never as "revert before starting").
4. **Coordination**: mail the coordinator the pointer path plus bead and branch.
