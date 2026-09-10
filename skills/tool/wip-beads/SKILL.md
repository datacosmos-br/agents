---
name: wip-beads
description: >
  Batch bead governance processor for FLEXT repos. Use when the user asks to
  update beads in bulk, reconcile workspace evidence into beads, classify
  bugfix/hotfix without epics, align tasks to a few canonical epics, unblock
  chains, or synchronize deferred statuses. Triggers: "atualize beads",
  "wip-beads", "classifique beads", "destrave", "--limits", "--beads",
  "workspace sync beads", batch CSV processing of tracker items.
---

# wip-beads — Continuous bead governance

## Canonical tool
`~/wip-beads.sh` — CSV-driven, batches of `--limits`, selects `--beads`,
modes: `collect|classify|align|unblock|title|deferred|all`, `--apply` for writes.
Default = dry-run. Logs under `~/.local/state/wip-beads/`.

## Input CSV
`~/wip-beads-cosmos-open.csv` — regenerate with:

    bd list --state open --json > ~/wip-beads-cosmos-open.json
    python3 - <<'EOF'
    import json, csv, os
    data = json.load(open(os.path.expanduser('~/wip-beads-cosmos-open.json')))
    rows = [['id','title','status','issue_type','priority','parent_id','labels','dep_count']]
    for b in data:
        rows.append([b['id'], b['title'], b['status'], b['issue_type'], b['priority'],
                     b.get('parent') or '', '|'.join(b.get('labels', [])),
                     b.get('dependency_count', 0)])
    csv.writer(open(os.path.expanduser('~/wip-beads-cosmos-open.csv'), 'w', newline='')).writerows(rows)
    EOF

## Governance law (strict)
1. Truth: every note carries command + evidence; never fake "resolved".
2. `bd` is the canonical ledger; never edit `.beads/` by hand.
3. `bugfix`/`hotfix`/`bug` beads: NO epic parent, ever. If they have one,
   the classify mode reports it for removal (operator confirms on apply).
4. `task`/`feature` beads: consolidated under FEW canonical epics —
   prefer the exact epic family over shallow parents.
5. Deferred (❄) beads get revalidation notes, not silent reopening.
6. Workspace evidence first: root+submodules+worktrees before any status
   write; the `collect` mode stamps `WORKSPACE SYNC` evidence.
7. Batches: >= 25 beads per batch; subagents execute batches, coordinator
   validates. One coordinator owns integration of results.

## Batch cycle loop
1. Regenerate CSV (source of truth of current open set).
2. `--mode classify` dry-run, review the desired parents report.
3. `--mode align` to re-parent tasks into canonical epics.
4. `--mode unblock` to print dependency chains and ready count.
5. `--apply` only after the operator (or coordinator agent) approves the plan.
6. Append every resulting note via `bd note` (never via file edits).

## Evidence format (bd note)
    WORKSPACE SYNC <ISO8601> (wip-beads.sh <mode> [apply|dry]): <what changed>
    beads=<n> batches=<n> apply=<0|1>

co-verified with `bd show <id>` output pasted when disputed.
