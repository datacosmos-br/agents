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
exists only where a declared migration leaves one at a tool's fixed path. Tool data
(package, interpreter and tool caches, downloads, `__pycache__`, the Testmon database)
lives once at each tool's default location, ignored by Git, and is reused by every run,
checkout and test; nothing copies or re-downloads it per run, and a run's temporary files
sit under the tool's own retention or are removed by that run, also when it is stopped.
Each checkout, or its declaring workspace, owns one physical `.venv`, built only by its
setup verb and never borrowed, copied or cleared while in use; local supplier checkouts
enter it only through the setup verb's supplier-root parameter.
