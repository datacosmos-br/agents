---
name: op-learning
description: "operator corrections, text replacement, governance reconciliation"
metadata:
  aihub.tags: '["decision:ADR-0038","effective:2026-11-03","supersedes:skill:operator-correction-learning","usage:router"]'
---

# Operator correction learning

Activate when the operator corrects behavior. The correction binds its stated scope and
grants no broader preference.

A correction replaces text; it never adds a clause, an evaluation role or a new rule. Find
the governing text it contradicts (rule, skill, ADR, AGENTS file, memory or plan), rewrite
that text at its single owner, and delete every opposite and every stale delivered copy
in the same change. The result is no longer than what it replaced. The operator's words live in
the tracker and the text cites the key (`rules/law.md` 12).

Write the general outcome, never the incident. A mutable value is named by its owner,
never copied; an invariant is stated once, at its owner.

Cite an operator decision only from the operator's own recorded words; anything else is
unverified. Two current corrections that conflict, or one that would change the agreed
specification, get one precise question with both texts before any edit.

When no governing text is wrong, change nothing.
