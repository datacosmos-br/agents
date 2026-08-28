---
name: strategic-compact
description: 'context compaction, execution continuity, session recovery'
metadata:
  aihub.tags: '["policy:atomic-effects","policy:fail-loud","policy:no-fallback","policy:preflight-before-effects","policy:strict-execution","provenance:agents-owned","role:continuity","updates:manual","usage:on-demand"]'
---

# Strategic Compact

Activate when a long session needs a durable context boundary or recovery packet.
Read the [complete procedure](references/procedure.md) before compacting and do
so only at a proven logical boundary. Do not use compaction to hide red gates,
unpublished WIP, or an unresolved owner decision.
