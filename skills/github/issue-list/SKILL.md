---
name: issue-list
description: "List GitHub issues as an ASCII box table. USE FOR: issue triage and tracking views with filters (--state --assignee --label --author --milestone --limit). DO NOT USE FOR: PRs (pr-list); mutating issues; posting comments."
license: MIT
metadata:
  bundle: github
  scope: universal
---

# Issue List

## Execution

1. `gh issue list` + filters, always with `--json number,assignees,labels,title,state`.
2. Render Unicode box table: right-align numbers, left-align text, pad columns.
3. Title ≤45 chars; first assignee or `-`; up to 2–3 labels abbreviated.
4. Footer: `**N issues** (M open, K closed)`.

```text
┌───────┬──────────┬─────────────┬──────────────────────────────────┬────────┐
│ Issue │ Assignee │ Labels      │ Title                            │ State  │
├───────┼──────────┼─────────────┼──────────────────────────────────┼────────┤
│   372 │ max      │ enhancement │ Create /issue-list skill         │ OPEN   │
└───────┴──────────┴─────────────┴──────────────────────────────────┴────────┘
```
