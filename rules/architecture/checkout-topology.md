---
description:
  Project kind decides who may rewrite a repository; forks follow upstream and no
  tracked symlink leaves a repository.
metadata:
  aihub.tags: '["decision:ADR-0038","effective:2026-11-03","route:both"]'
---

# Project kind and checkout topology

Each repository declares one kind, never inferred: `internal_flext`, `internal` or
`third_party_fork`. Generators rewrite only `internal_flext`, and none whose kind is
unreadable. A fork follows its upstream except in source identity, delta provenance,
artifact integrity, deployment configuration and runtime proof. Internal code and tools
target the manifest's runtime floor natively, with precise types. A repository is
`workspace` (declares `.gitmodules`) or `standalone` and reaches outside itself only
through declared configuration, never a tracked symlink ([law](../law.md) 6).
