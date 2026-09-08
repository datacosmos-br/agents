---
name: pr-list
description: List GitHub pull requests with review, check, and merge state preserved.
argument-hint: "<repository and optional gh pr list filters>"
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-08-29","route:agent"]'
---

# GitHub pull request list

Treat `$ARGUMENTS` as an explicit repository plus optional `gh pr list`
filters. Require the repository and reject unknown flags, malformed limits, or
an ambiguous target before contacting GitHub.

1. Confirm that `gh` is installed and authenticated without revealing secrets.
   Authentication, network, authorization, and API failures remain nonzero.
2. Accept only documented read filters such as state, author, assignee, label,
   search, base, head, draft, and limit. Never evaluate user text as shell code.
3. Request structured fields sufficient to preserve number, title, author,
   state, draft state, review decision, merge state, checks, base/head, URL, and
   update time.
4. Render every returned PR in a deterministic Unicode table and summarize open,
   draft, approved, changes-requested, blocked, and failing-check states. Never
   hide `CHANGES_REQUESTED`, red checks, or merge conflicts by default.

Return the repository, filters, complete returned count, and table. An empty
list is green only when the authenticated query itself succeeded.
