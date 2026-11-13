---
description:
  A managed fork versions itself as its measured upstream release plus a local suffix.
metadata:
  aihub.tags: '["decision:ADR-0038","effective:2026-11-03","route:both"]'
---

# Fork version locality

A managed fork's version is the latest published upstream release plus a local suffix:
`+dc.N` (PEP 440) for Python, `-fc.N` where the ecosystem uses that form. That release
is measured from the upstream release API, tags or manifest when the fork release is
cut, never recalled or taken from a branch, PR or draft. N grows by one per fork release
and restarts at 1 when a new upstream release is merged in with `git merge --no-ff`. All
version surfaces agree, and tests and docs use the current scheme or an explicitly fake
version, never an invented one.
