---
description:
  Remote access follows the declared Git identity; agents never write SSH configuration.
metadata:
  aihub.tags: '["decision:ADR-0038","effective:2026-11-03","route:both"]'
---

# Remote identity

Remote access uses the repository's declared Git and forge identity. Agents never
rewrite remote protocols, create identity aliases or write the operator's SSH
configuration or keys; a broken identity is repaired in Git or reported to the operator,
never replaced by a generic remote.
