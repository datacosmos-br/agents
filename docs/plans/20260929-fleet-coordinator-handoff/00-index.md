# 20260929: fleet coordinator handoff (index)

This is the canonical handoff for the next fleet-coordinator session. Every fact
was measured on this host between 2026-09-29T00:45Z and 01:30Z. Execution state
is held in Beads; this directory holds only pointers and rulings.

## Read order

1. [`handoff.md`](handoff.md): mission, rulings, laws, resume queue, pending
   operator decisions, and a condensed critique of the previous coordinator
   window.
2. The owning beads named in `handoff.md`. Run `bd show <id>` in each rig
   through `direnv exec <rig-home>`.
3. `docs/rules/session-execution-rules-20260927.md` (R-S1..) and
   `rules/coordination/heavy-gate-serialization.md`.

## Pointers

- Root execution epic: `flext-itpd1`. Its notes carry this path.
- Home pointer (read by `commands/governance/session-startup.md`):
  `~/.claude/plans/handoff-20260929-fleet-coordinator.md`.
- Coordination: the `gc mail` subject `[coord] HANDOFF` sent to `human`.
- Governance defects filed in the agents store: `ag-k47r`, `ag-g29z`, `ag-e3ul`,
  `ag-h31o`, `ag-c0vo`, `ag-4a82`, `ag-xd1y`.
