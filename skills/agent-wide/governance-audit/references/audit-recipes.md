# Audit Recipes (beads/audit)

Copy-paste checks for the tracker hygiene checklist in `../SKILL.md`.
Read-only: every command here is inspection, never mutation.

## Tracker State

```bash
set -euo pipefail

# Totals and distribution
bd stats
bd list --status open --json | jq -r 'group_by(.issue_type) | .[] | "\(.[0].issue_type): \(length)"'
bd list --status open --json | jq -r 'group_by(.priority) | .[] | "P\(.[0].priority): \(length)"'

# Claim concentration (who owns the board)
bd list --status open --json | jq -r 'group_by(.assignee // "none") | .[] | "\(.[0].assignee // "none"): \(length)"'

# in_progress AND dep-blocked (state conflict)
in_progress_ids="$(
  bd list --status in_progress --json | jq -r '.[].id' | sort
)"
blocked_ids="$(
  bd blocked --json | jq -r '.[].id' | sort
)"
comm -12 \
  <(printf '%s' "$in_progress_ids") \
  <(printf '%s' "$blocked_ids")

# Stale blocked: status=blocked but no open blocker
bd list --json | jq -r '.[] | select(.status=="blocked") | .id' | while read -r id; do
  bd show "$id" --json | jq -r '.[0] | "\(.id): \(.dependencies // [] | map(.id) | join(","))"'
done   # then bd show each listed blocker: closed target = stale dep

# NULL epic descriptions
bd list --json | jq -r '.[] | select(.issue_type=="epic" and .status=="open" and (.description == null or .description == "")) | .id'

# Bulk-touch detection (timestamps useless)
bd list --status open --json | jq -r '[.[].updated_at[0:10]] | unique | length'
# 1 = bulk-touched: audit CONTENT, not dates

# Epic health
bd epic status
# >=70% children closed with <=2 open = drain candidate; two epics sharing
# directive keywords = fold candidate (orchestrator decision)
```

## Content Staleness

```bash
set -euo pipefail

# Dead file references in descriptions (run per suspicious path)
ls <referenced-path>

# Closed ancestors cited as live context
bd show <cited-id> --json | jq -r '.[0].status'

# Notes archaeology (synthesis missing from description)
bd show <id> --json | jq -r '.[0].notes | length'   # hundreds = archaeology
```

## Dual Paths And Projections

```bash
set -euo pipefail

ls -d <path-a> <path-b>        # both exist = dual-path finding
diff -rq <canonical> <projection>   # source vs projection drift
```

## Finding Severity Guide

- **P0**: dual orchestrators mutating, bead with no owner mid-flight, SSOT
  divergence (two truths).
- **P1**: stale blocks hiding ready work, NULL epic descriptions, claim
  concentration, zombie lanes.
- **P2**: priority inflation, note archaeology, dead doc references.

Report as: check | finding | evidence (command + decisive output) | proposed
action | severity — to the orchestrator. You never enact semantic changes.

## Docs Freshness vs Reality (UNIVERSAL_CORE 14)

- README/AGENTS.md links: follow each canonical link; stale target = finding.
- Command references: run 2-3 documented commands with `--help`; mismatch
  between doc and live CLI = finding.
- Structure claims (dirs, module counts, LOC): spot-check against the tree.
- Version/date headers older than the last structural change = suspect;
  sample one claim for reality drift.
- Report severity P1 for canonical-link rot, P2 for prose drift.
