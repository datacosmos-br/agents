---
description: Dispatch independent bulk work to fast parallel subagents; the main thread owns sequenced effects.
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

Bulk, independent work — sweeps, batch revalidations, inventories, research,
bookkeeping — is delegated to fast parallel subagents, one bounded assignment
each. Verify every subagent result against reality before accepting it; an
empty or asserted result is not a claim.

The main thread alone owns sequenced effects: operator decisions, merges,
landings, and tracker closure with evidence. Never delegate a sequenced effect,
and never serialize work whose steps share no state.

Compose with `shared-file coordination` (rule file),
`session governance` (rule file), and
`bead verification` (rule file).
