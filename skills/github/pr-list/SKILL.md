---
name: pr-list
description: "List GitHub pull requests as an ASCII box table. USE FOR: PR review workflows and sheriff duty views with filters (--state --author --label --draft --limit). DO NOT USE FOR: issues (issue-list); triage decisions (pr-sheriff); merging."
license: MIT
metadata:
  bundle: github
  scope: universal
---

# PR List

## Execution

1. `gh pr list` + filters, always with `--json number,author,title,state,isDraft,reviewDecision`.
2. Exclude `reviewDecision=CHANGES_REQUESTED` unless `--all-reviews`.
3. Render Unicode box table: right-align numbers, left-align text, pad columns.
4. Title ≤50 chars; author ≤18 chars; state `OPEN/CLOSED/MERGED/DRAFT`.
5. Footer: `**N open PRs** (M drafts)`.

```text
┌─────┬──────────────┬─────────────────────────────────────────┬────────┐
│  PR │ Author       │ Title                                   │ State  │
├─────┼──────────────┼─────────────────────────────────────────┼────────┤
│ 123 │ username     │ feat: add new feature                   │ OPEN   │
│ 122 │ another-user │ fix: resolve bug                        │ DRAFT  │
└─────┴──────────────┴─────────────────────────────────────────┴────────┘
```
