---
name: wip-beads
description: 'wip beads, batch governance, csv workflow, classify align apply'
metadata:
  aihub.tags: '["activation:opt-in","decision:ADR-0008","detect:opt-in:wip-beads","effective:2026-09-10","route:agent","subject:beads","usage:router"]'
---

# wip-beads — Continuous bead governance

## What this is and when to reach for it

`scripts/wip-beads.sh` (in this skill bundle) is a batch processor over the `bd` ledger. Use it when bead
work is REPETITIVE (dozens of beads need the same check or mutation) — never
for one-off edits (a single `bd update` is faster and safer).

Why a script instead of hand-run `bd` commands: hand editing 100 beads leaks
three failure classes the script closes — skipped beads (no inventory), silent
half-batches (no resumo), and undocumented mutations (no per-bead evidence
line). The script processes an inventory, prints per-bead decisions, and ends
with a countable resumo. Everything runs dry-run until you pass `--apply`.

## Canonical tool

`scripts/wip-beads.sh` (in this skill bundle) — CSV-driven, batches of `--limits`, selects `--beads`,
modes: `collect|classify|align|unblock|title|deferred|all`, `--apply` for writes.
Flags: `--csv` (input CSV path), `--beads` (comma-separated IDs), `--limits` (batch sizes), `--apply` (mutate), `--map` (align map CSV: `bead_id,desired_parent`), `--json-report` (output report path).
Default = dry-run. Logs under `${XDG_STATE_HOME:-$HOME/.local/state}/wip-beads/` (the script's declared state root).

## Modes explained (what each one answers)

| Mode | Question it answers | Mutates (with --apply) |
|---|---|---|
| `collect` | Did the ledger drift from my CSV snapshot since I started? | `bd note` WORKSPACE SYNC only on drifted beads |
| `classify` | Do bug/hotfix beads illegally carry an epic parent? | removes parent (`bd update --parent ""`) |
| `align` | Do tasks/features sit under the right canonical epic? | re-parents per `--map` file |
| `unblock` | Which blocked beads are waiting on already-closed blockers? | nothing — report only |
| `title` | Are titles WIP-free and labels convention-clean? | `bd update --title` |
| `deferred` | Which deferred beads need a revalidation decision? | `bd note` revalidation |
| `all` | Run the six above in sequence | any of the above |

Read the CSV columns as your pre-flight inventory: `status`/`parent_id` come
from the moment you generated the file — every mode compares CSV vs live
ledger and reports the delta instead of trusting either side blindly.

## Reading the output

Per bead, one of four lines:

- `[SKIP <mode>] <id>: <reason>` — nothing to do, reason states the compared values.
- `[<mode>] <id>: <plan>` — dry-run: what `--apply` WOULD run.
- `[DRY-RUN <mode>] <id>: <cmd>` — the exact command queued for apply.
- `[APPLIED <mode>] <id>` — mutation executed (only with `--apply`).

The batch ends with `--- RESUMO <mode>: processed=<n> mutated=<n> errors=<n> skipped=<n> ---`.
A healthy dry-run has `errors=0`; `mutated` counts PLANNED changes. Before any
`--apply`, that number is your blast radius — review it, don't skip it.

## Input CSV

`./wip-beads-open.csv` — regenerate with:

    bd list --status open --flat --limit 0 --json > ./wip-beads-open.json
    python3 - <<'EOF'
    import json, csv, os
    data = json.load(open(os.path.expanduser('./wip-beads-open.json')))
    rows = [['id','title','status','issue_type','priority','parent_id','labels','dep_count']]
    for b in data:
        rows.append([b['id'], b['title'], b['status'], b['issue_type'], b['priority'],
                     b.get('parent') or '', '|'.join(b.get('labels', [])),
                     b.get('dependency_count', 0)])
    csv.writer(open(os.path.expanduser('./wip-beads-open.csv'), 'w', newline='')).writerows(rows)
    EOF

## Governance law (strict)

1. Truth: every note carries command + evidence; never fake "resolved".
2. `bd` is the canonical ledger; never edit `.beads/` files by hand — the Dolt
   DB owns the state, the JSONL files are passive exports.
3. `bugfix`/`hotfix`/`bug` beads: NO epic parent, ever. Why: bugs are fleet-wide
   defects, not planned epic scope; parenting one hides it inside a delivery
   epic's "done" story. The classify mode reports the parent for removal;
   operator confirms on apply.
4. `task`/`feature` beads: consolidated under FEW canonical epics —
   prefer the exact epic family over shallow parents. Why: many shallow parents
   fragment the ready-queue and hide blocked chains.
5. Deferred (❄) beads get revalidation notes, not silent reopening.
6. Workspace evidence first: root+submodules+worktrees before any status
   write; the `collect` mode stamps `WORKSPACE SYNC` evidence.
7. Batches: >= 25 beads per batch; subagents execute batches, coordinator
   validates. One coordinator owns integration of results.
8. Close only with 3 legal reasons: `SUPERSEDED` (canonical owner named absorbs),
   `OBSOLETE` (scope/explicit disappeared with proof), `DONE` (cmd/cwd/exit/output).
   `LEGITIMATE` = comment both, DO NOT close.
9. Cap 20 closes per batch (`bd batch`); re-run dedup gate + `bd doctor --check=validate`
   - `bd orphans` after each batch.
10. Never mutate beads of ACTIVE third-party lanes (from §0.7 + claims ≤24h).

## Known failure modes (learned 2026-09-10 cycle)

- **Label case corruption**: label "standardization" that lowercases
  `priority:P0` → `priority:p0` CORRUPTS convention (project labels are
  case-sensitive). A title-normalize pass mutated 40 beads this way; the fix
  preserves case (trim+dedup only). Never let a normalizer change the case of
  existing label values.
- **Status drift between CSV and ledger**: the snapshot ages the moment you
  write it. Every mode re-reads the live ledger and compares; a `mutated=19`
  on collect means 19 beads drifted since the CSV was generated — audit before
  applying, drift is often another lane's legitimate work.
- **`bd show` per bead is the bottleneck**: ~3.5s/call × 100 beads ≈ 6min/mode.
  One `bd list --all --flat --limit 0 --json` snapshot per mode cuts this to
  ~20s. See Performance below.
- **Counter increments under `set -e`**: `((counter++))` exits 1 when the
  counter is 0 and kills the script mid-batch. Use `((counter+=1)) || true`.
  (Kept here because any fork of this script tends to reintroduce it.)

## Performance

At the start of each mode, make one SSOT ledger fetch:
`bd list --all --flat --limit 0 --json` (the required form of
`bd list --all --flat --json`), index it by id, and reuse that snapshot for the
whole mode. Call `bd show --json` for a bead only when its id is absent. Refresh
between modes; never reuse a stale snapshot.

Measured effect on a 102-bead ledger: `classify` 6min → 20.4s.

## Worked example (dry-run → apply, one epic realign)

    # 1. inventory
    bd list --status open --flat --limit 0 --json > ./wb.json   # + CSV convert (workspace-local)
    # 2. plan
    scripts/wip-beads.sh --mode align --map ./epics-map.csv --beads "<bead-id>"
    #    → [align] <bead-id>: parent atual=vazio desejado=<canonical-epic-id>
    # 3. one bead, confident, small blast radius:
    scripts/wip-beads.sh --mode align --map ./epics-map.csv --beads "<bead-id>" --apply
    #    → [APPLIED align] <bead-id>
    bd show <bead-id> --json | jq -r '.[0].parent'   # → <canonical-epic-id> (verify, never trust)

Verification after apply is part of the mode, not optional: the script's own
output is intent, `bd show` is the truth.

## Deep-clean

Run `bd doctor --check=validate --json`, `bd doctor --check=pollution --json`,
and `bd orphans --json` after the batch.

These three gates answer different questions — do not conflate them:

- `doctor` asks "is the ledger internally consistent?" (0 failed AND 0 warnings).
- `pollution` asks "did test artifacts leak into the production ledger?" It
  counts but does NOT list IDs.
- `orphans` asks "which open beads does git history reference?" — it is a
  commit-cross-reference, NOT a dependency-graph defect report.
- **Test pollution**: doctor reports a count without listing IDs. The detection
  criterion (extracted from bd 1.2.2) is a title regex `^test[-:]`
  case-insensitive — legitimate beads like "test-law: ..." false-positive on it.
  Enumerate the complete ledger with `bd list --all --flat --limit 0 --json`,
  reproduce the criterion, inspect each hit with `bd show <id> --json`. A real
  artifact closes with `bd close <id> --force --reason "OBSOLETE: test artifact; see bd show <id>"`
  (cap 20/batch); a false positive gets its TITLE reworded past the regex —
  renaming preserves the description and clears the flag without touching
  closed-bead history.
- **Orphans**: `bd orphans` identifies commit-referenced issues still
  open/in_progress, not dependency-graph defects. Two distinct causes, two
  distinct fixes: (a) the commit delivered only a SLICE of the bead's scope —
  keep the bead open and justify the flag with a `bd note` naming the delivered
  slice and the missing acceptance criteria (closing here is a false green);
  (b) the commit fully delivered it — close with DONE + cmd/cwd/exit/output.
  Repair graph defects at the cause: `bd update <id> --parent <canonical>` or
  `bd dep remove <id> <dead-id>`, then rerun both gates.
- **Status-delta audit**: after each batch compare the pre-cycle CSV with a fresh
  `bd list --all --flat --limit 0 --json` snapshot. Classify every status change
  as external lane activity (check `updated_at` + owner) or an effect of this
  cycle; record external activity and correct unintended cycle effects forward.
  No unclassified drift. Why: your apply ran against a world other sessions are
  also mutating; the audit is how you prove you touched only what you planned.

## Batch cycle loop

1. Regenerate CSV (source of truth of current open set).
2. `--mode classify` dry-run, review the desired parents report.
3. `--mode align` to re-parent tasks into canonical epics.
4. `--mode unblock` to print dependency chains and ready count.
5. `--apply` only after the operator (or coordinator agent) approves the plan.
6. Append every resulting note via `bd note` (never via file edits).

Why this order: classify defines WHAT each bead is, align defines WHERE it
lives, unblock reads the graph those two just cleaned. Applying classify before
review would strip parents from bugs that may instead need re-homing — the
dry-run report is where that nuance surfaces.

## Subagent batch protocol

Coordinator generates CSV → splits into batches via `--limits` → each subagent
runs dry-run on its batch → coordinator reviews consolidated dry-run output →
operator/coordinator approves → `--apply` executes batch → coordinator appends
evidence note per bead (`WORKSPACE SYNC <ISO8601> (wip-beads.sh <mode> [apply|dry]): <what changed>; beads=<n> batches=<n> apply=<0|1>`).

Rule for subagents: they execute batches, they never decide policy. Any bead
whose dry-run output looks wrong (unexpected parent, unexpected status) goes
back to the coordinator, not into a "fix it while I'm here" mutation. One
writer at a time: the coordinator runs `--apply`, subagents stay dry-run.

## Evidence format (bd note)

    WORKSPACE SYNC <ISO8601> (wip-beads.sh <mode> [apply|dry]): <what changed>
    beads=<n> batches=<n> apply=<0|1>

Co-verified with `bd show <id>` output pasted when disputed.

(End of file)
