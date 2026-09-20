---
description:
  Dispatch independent bulk work to fast parallel subagents; the main thread owns
  sequenced effects.
capsule_summary: |
  Bulk, independent work — sweeps, revalidations, inventories, research,
  bookkeeping — is delegated to fast parallel subagents, one bounded assignment
  each, with every result verified before acceptance; an empty subagent result
  is not a claim. The main thread alone owns sequenced effects: operator
  decisions, merges, landings, and tracker closure with evidence. Never
  delegate a sequenced effect, and never serialize work that shares no state.
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-09-10","route:both"]'
---

# Dispatch independent work to fast parallel subagents

Bulk, independent work — sweeps, batch revalidations, inventories, research, bookkeeping
— is delegated to fast parallel subagents, one bounded assignment each. Verify every
subagent result against reality before accepting it; an empty or asserted result is not
a claim.

The main thread alone owns sequenced effects: operator decisions, merges, landings, and
tracker closure with evidence. Never delegate a sequenced effect, and never serialize
work whose steps share no state.

Compose with `shared-file coordination` (rule file), `session governance` (rule file),
and the tracker-verification rule.

## Model and effort selection follows the cost matrix (operator ruling, 2026-09-12)

<!-- Why: registers 2026-09-12 operator ruling R27 on this file, the existing subagent-dispatch owner -->

Route subagent dispatch by a cost index, not by habit: relative price weight Haiku 4.5 =
0.5, Sonnet 5 = 1, Opus 5 = 2.5, Fable 5.1 = 5, multiplied by an effort factor (low ≈
0.25, medium ≈ 0.5, high = 1). Mechanical or bounded work (search, read, verify) goes to
Haiku at low effort or Sonnet at medium; routine edits and multi-file feature work go to
Sonnet at medium or high; hard debugging, refactors, and architecture decisions go to
Opus at high effort; Fable is reserved for long-horizon work at low or medium effort
only. Decisions, merges, and operator dialogue never delegate — they stay with the
coordinator regardless of cost.
