---
name: strategic-compact
description: 'context compaction, execution continuity, session recovery'
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-08-29","usage:on-demand"]'
---

# Strategic Compact

Activate when a long session needs a durable context boundary or recovery packet.
Read the `complete procedure` (skill file) before compacting and do
so only at a proven logical boundary. Do not use compaction to hide red gates,
unpublished WIP, or an unresolved owner decision.
When a handoff has a file-owned plan, transfer through `plan-handoff`, not a
source transcript.
