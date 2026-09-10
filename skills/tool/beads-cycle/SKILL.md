---
name: beads-cycle
description: 'beads cycle, continuous governance, csv workflow, classify align unblock'
metadata:
  aihub.tags: '["activation:opt-in","decision:ADR-0008","detect:opt-in:beads-cycle","effective:2026-09-10","route:agent","subject:beads","usage:router"]'
---

# beads-cycle — Continuous bead governance cycle

## What this skill is

The operating rhythm that keeps a `bd` ledger from rotting: regenerate the
inventory, reconcile it against the live workspace, classify and re-home beads,
verify integrity, and record evidence — in one repeatable cycle. Run it after
every large delivery wave, before backlog triage, or whenever
`bd doctor`/`bd stats` look wrong.

Relationship to sibling skills: `wip-beads` owns the TOOL reference (flags,
output semantics, failure modes); this skill owns the CYCLE (order, gates, who
decides). When both apply, follow the order here and the tool detail there.

## Why the order is fixed

Each step shrinks the search space of the next: collect reconciles reality
first (so classify/align judge live truth, not stale CSV), classify defines
WHAT a bead is, align defines WHERE it lives, unblock reads the graph those
two just cleaned, title/deferred polish what remains, and the deep-clean gates
only pass on a ledger already consistent. Skipping ahead produces rework: a
title pass before classify renames beads that classify is about to re-parent.

## Canonical flow
`~/wip-beads.sh` with modes `collect|classify|align|unblock|title|deferred|all`
and flags `--csv --beads --limits --apply --map --json-report`.

## Cycle steps (execute in order)

### 1. Regenerate CSV (source of truth)
```bash
bd list --status open --flat --limit 0 --json > ~/wip-beads-cosmos-open.json
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

### 8. Doctor deep-clean (test pollution + orphans)
```bash
bd doctor --check=validate --json
bd doctor --check=pollution --json
bd orphans --json
```
- **Test pollution**: `validate`/`pollution` reports a count but does not
  identify IDs. The detection criterion (extracted from bd 1.2.2) is a TITLE
  regex `^test[-:]`, case-insensitive — so legitimate beads like
  "test-law: ..." false-positive on it. Enumerate the complete ledger with
  `bd list --all --flat --limit 0 --json`, reproduce the criterion, inspect
  each hit with `bd show <id> --json`. A proven artifact closes (max 20/batch):
  `bd close <id> --force --reason "OBSOLETE: test artifact; see bd show <id>"`.
  A false positive gets its TITLE reworded past the regex — renaming preserves
  the description and clears the flag without touching closed history.
- **Orphans**: `bd orphans` reports commit-referenced issues that remain
  open/in_progress; it is not itself a dependency-graph report. Two causes,
  two fixes: (a) the referenced commit delivered only a SLICE of scope — keep
  the bead open and justify the flag with `bd note` (closing = false green);
  (b) fully delivered — close DONE with cmd/cwd/exit/output. True graph
  defects get fixed at the cause: `bd update <id> --parent <canonical>` or
  `bd dep remove <id> <dead-id>`. Re-run both gates until clean or each
  exception is justified on the coordinator bead.
- **Status-delta audit**: after every batch, diff the pre-cycle CSV against a
  fresh `bd list --all --flat --limit 0 --json` snapshot. Classify each status
  change as external lane activity (`updated_at` + owner) or an effect of this
  cycle; record the former, revert the latter. No unclassified drift — this is
  the proof you touched only what you planned.

### 9. Validate (mandatory after each batch)
```bash
bd doctor --check=validate          # zero errors AND zero warnings required
bd find-duplicates --status open --limit 50 --json  # output must be empty
bd orphans                          # zero new orphans
```
Why these three: doctor proves internal consistency, dedup proves one survivor
per concept, orphans proves git history agrees with the ledger. A batch that
skips them can have "succeeded" while corrupting the graph.
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

## Performance law (SSOT fetch)
One ledger fetch per mode, not per bead: load a single
`bd list --all --flat --limit 0 --json` snapshot at mode start and index it by id.
Per-bead `bd show` is a fallback only for ids missing from the snapshot.
Re-fetch the snapshot between modes, never reuse stale.
Measured on a 102-bead ledger: one `bd show` ≈ 3.5s, so per-bead fetches cost
~6min per mode while a single snapshot runs the same mode in ~20s.

## Evidence format (bd note)
```
WORKSPACE SYNC <ISO8601> (wip-beads.sh <mode> [apply|dry]): <what changed>
beads=<n> batches=<n> apply=<0|1>
```
Co-verified with `bd show <id>` output when disputed. The note is the audit
trail: months later, "why does this bead have no parent?" is answered by this
line plus the classify dry-run log, not by memory.

## Completion criteria
- `bd doctor --check=validate` = 0 errors AND 0 warnings
- `bd find-duplicates` = zero unadjudicated pairs
- `bd orphans` = zero new orphans (each retained flag justified on the coordinator bead)
- Non-closed count ≤ 20% of baseline OR justified retention per family recorded
- All decisions documented on coordinator bead + snapshot saved

A cycle that ends with any gate red is NOT done — it is a documented handoff
with the failure named, owned, and queued.

(End of file)