---
description: Where paths, scratch state, caches and Python environments live
metadata:
  aihub.tags: '["decision:ADR-0038","effective:2026-11-03","route:both"]'
---

# Storage

One typed storage owner per project validates every physical path before effects and
stages on the destination filesystem. `/tmp` holds no working checkout, environment,
persistent database, cache, checkpoint or report, and no backup, archive, quarantine
copy or `.bak` sibling exists anywhere: Git history is the recovery. A committed file
holds no private absolute path or reference into another checkout, and a symbolic link
exists only where a declared migration leaves one at a tool's fixed path. Caches
and downloads live once at tool defaults for every checkout, `__pycache__` and the
Testmon database in their checkout; all are reused, never copied or tracked; a run
removes its own temporary files, also when stopped, or leaves them to the tool's retention.
Each checkout, or its declaring workspace, owns one physical `.venv`, built only by its
setup verb and never borrowed, copied or cleared while in use; local supplier checkouts
enter it only through the setup verb's supplier-root parameter.
