---
description: Mutação consumer-facing gates on a decision; discovery work never does
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-09-11","route:both"]'
---

# Discovery never blocks; mutation does

When a convergence plan waits on an operator decision (an A/B/C on, say, renaming
consumer-facing facade classes), the temptation is to idle the whole lane. In the
cosmos-3flk9 sweep the fleet-wide namespace surf (~1.4k errors) sat behind an operator
decision for an entire cycle while the harmless inventory work that would have made the
decision cheap sat undone.

- Split every blocked decision into (1) read-only discovery that can start immediately —
  consumer inventories, cost tables, runtime contract audits — and (2) mutation that
  genuinely requires the decision/authority gate.
- Present decisions WITH pre-costed data from the discovery: option A/B/C each carrying
  its measured class count, consumer count, and break risk.
- The operator decision then executes in hours, not days.
- Discovery output is stored in the epic it serves, so the decision context survives
  session handoff.

See also: `phase-admission-protocol.md` (rule file), `production-readiness.md` (rule
file).
