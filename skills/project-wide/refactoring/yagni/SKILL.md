---
name: yagni
description: 'speculative scope, current consumers, necessity analysis'
license: MIT
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-08-29","usage:router"]'
  version: 1.1.0
---

# YAGNI

Remove behavior, options, abstractions, dependencies, extension points, and
compatibility surfaces that lack a current requirement, current consumer, and
reachable supported runtime. Every retained concept must justify existence now.
An environment variable, setting, parameter, or argument that only repeats a
canonical calculated default has no independent requirement and is removed.

Consume the `search-first` evidence packet, apply the
`necessity procedure` (skill file), and pass only the surviving
concept set to `ssot`. YAGNI decides existence, not authority or design.

Do not delete a real public contract, rare current consumer, security control,
required migration, or operational invariant. Missing ownership, callers,
acceptance criteria, or runtime evidence blocks deletion.
