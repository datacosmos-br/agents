---
name: beads-cycle
description: 'beads cycle, continuous governance, csv workflow, classify align unblock'
metadata:
  aihub.tags: '["activation:opt-in","decision:ADR-0008","detect:opt-in:beads-cycle","effective:2026-09-10","route:agent","subject:beads","usage:router"]'
---

# beads-cycle — Continuous bead governance cycle

## Canonical flow
`~/wip-beads.sh` with modes `collect|classify|align|unblock|title|deferred|all`
and flags `--csv --beads --limits --apply --map --json-report`.

## Cycle steps (execute in order)

### 1. Regenerate CSV (source of truth)
```bash
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
```

### 2. Collect workspace evidence
`~/wip-beads.sh --mode collect --csv ~/wip-beads-cosmos-open.csv`
- Scans root repo + submodules (`apps/cosmos-charts`, `apps/cosmos-gitops`) + active worktrees
- Stamps `WORKSPACE SYNC` evidence via `bd note` per bead
- Output: updated CSV with `workspace_evidence` column

### 3. Classify bugfix/hotfix/bug (no epic)
`~/wip-beads.sh --mode classify --csv ~/wip-beads-cosmos-open.csv`
- Reports beads with `issue_type` in {bugfix,hotfix,bug} that have a parent epic
- Dry-run by default; `--apply` removes parent after operator approval
- Law: `bugfix`/`hotfix`/`bug` beads NEVER have epic parent

### 4. Align tasks/features to canonical epics
`~/wip-beads.sh --mode align --csv ~/wip-beads-cosmos-open.csv`
- Re-parents `task`/`feature` beads under FEW canonical epic families
- Prefers exact epic family from latest plan (§0.4/§0.7) over shallow parents
- One canonical survivor per concept (ADR/plan-defined)

### 5. Unblock dependencies
`~/wip-beads.sh --mode unblock --csv ~/wip-beads-cosmos-open.csv`
- Prints dependency chains and ready count (zero deps = ready)
- Identifies blocked beads and their blockers
- Output: ready list for next execution wave

### 6. Improve titles/tags
`~/wip-beads.sh --mode title --csv ~/wip-beads-cosmos-open.csv`
- Normalizes titles to pattern: `[area] <imperative verb> <object>`
- Adds/aligns labels: `P0`–`P3`, `area:<domain>`, `type:<issue_type>`
- Removes stale/duplicate tags

### 7. Adjust deferred statuses
`~/wip-beads.sh --mode deferred --csv ~/wip-beads-cosmos-open.csv`
- Deferred (❄) beads get revalidation notes, not silent reopening
- If revalidation proves scope alive → remove deferred, add evidence note
- If scope gone → close `OBSOLETE` with proof

### 8. Validate (mandatory after each batch)
```bash
bd doctor --check=validate          # zero errors required
bd find-duplicates --status open --limit 0 --json  # zero unadjudicated pairs
bd orphans                          # zero new orphans
```
- Cap 20 closes per batch (`bd batch`)
- Re-run dedup gate + validation after each batch
- Record pre/post counts on coordinator bead

## Governance law (from plans 1788975913248, 1788980150347)
1. **Close only with 3 legal reasons**: `SUPERSEDED` (canonical owner named absorbs),
   `OBSOLETE` (scope/explicit disappeared with proof), `DONE` (cmd/cwd/exit/output).
   `LEGITIMATE` = comment both, DO NOT close.
2. **Zero parent closed with child pending** — check `↳` in `bd show` parent before close;
   re-home child by child (`bd update <child> --parent <owner>`), no batch.
3. **One canonical survivor per family** — defined by newest plan (ADR/§0.4/§0.7).
   Others close with survivor name in `--reason`.
4. **Cap 20 closes per batch** + validation gates.
5. **Never mutate active third-party lanes** (from §0.7 + claims ≤24h).
6. **Workspace evidence first** — root+submodules+worktrees before any status write.
7. **Subagent batch protocol**: coordinator generates CSV → splits via `--limits` →
   subagents dry-run per batch → coordinator reviews → `--apply` → evidence note per bead.

## Evidence format (bd note)
```
WORKSPACE SYNC <ISO8601> (wip-beads.sh <mode> [apply|dry]): <what changed>
beads=<n> batches=<n> apply=<0|1>
```
Co-verified with `bd show <id>` output when disputed.

## Completion criteria
- `bd doctor --check=validate` = 0 errors
- `bd find-duplicates` = zero unadjudicated pairs
- `bd orphans` = zero new orphans
- Non-closed count ≤ 20% of baseline OR justified retention per family recorded
- All decisions documented on coordinator bead + snapshot saved

(End of file)