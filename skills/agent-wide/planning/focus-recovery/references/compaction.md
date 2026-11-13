# Strategic Compact

Activate when a long session needs a durable context boundary or recovery packet. Read
the [compaction procedure](compaction-procedure.md) before compacting and do so only at a proven
logical boundary. Do not use compaction to hide red gates, unpublished WIP, or an
unresolved owner decision. When a handoff has a file-owned plan, transfer through
`plan-handoff`, not a source transcript.
