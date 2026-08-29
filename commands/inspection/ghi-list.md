---
name: ghi-list
description: List GitHub issues with explicit filters and an evidence-preserving terminal table.
argument-hint: "<repository and optional gh issue list filters>"
metadata:
  aihub.tags: '["intent:inspection","risk:external","route:agent"]'
---

# GitHub issue list

Treat `$ARGUMENTS` as an explicit repository plus optional `gh issue list`
filters. Require the repository; reject unknown flags, malformed limits, or an
ambiguous target before contacting GitHub.

1. Confirm that `gh` is installed and authenticated without printing credential
   material. Preserve authentication, network, authorization, and API failures
   as nonzero results.
2. Allow only documented read filters such as state, assignee, author, label,
   milestone, search, and limit. Do not pass user text through shell evaluation.
3. Request at least number, title, state, assignees, labels, URL, and updated time
   as structured JSON. Do not omit records merely because an assignee, label, or
   optional field is absent.
4. Render a deterministic Unicode table with right-aligned issue numbers,
   readable bounded columns, full URLs available outside truncated display
   fields, and a summary by state. State every applied filter.

Return the exact repository, filters, item count, and table. Empty results are a
valid result only after a successful authenticated query; a failed query must
never be rendered as an empty green table.
