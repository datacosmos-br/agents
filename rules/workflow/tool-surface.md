---
description: Evidence is read and edited through the agent's dedicated file tools, not shell text utilities
metadata:
  aihub.tags: '["decision:ADR-0038","effective:2026-11-20","route:both"]'
---

# Tool surface

When the agent runtime provides dedicated file tools (read, glob, search, edit), evidence
is read, searched and edited through them; `cat`, `head`, `tail`, `find`, `grep`, `sed`
and `awk` are not used for evidence or edits beside them. A runtime without such tools
uses its declared filter (`rtk`) on the native command.
