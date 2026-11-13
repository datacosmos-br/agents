---
name: search-first
description: "decision order, native tools, owner reuse, smallest new code"
license: MIT
metadata:
  aihub.tags: '["decision:ADR-0038","effective:2026-11-03","usage:router"]'
  version: 2.0.0
---

# Search First

Before changing code or configuration, take the first of these that gives the correct
behavior (`rules/law.md` laws 2 and 3):

1. Delete the need, or do nothing.
2. Use the declared tool or dependency that owns the job.
3. Extend the existing owner and rewire its consumers.
4. Write the smallest new code that a current consumer needs.

Each choice rests on a search of the repository, its pinned dependencies and their
documentation, never on an assumption. Report the choice and the owner it used.
