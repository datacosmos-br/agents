# Consolidation Reference (orchestrator)

Companion procedure to the local `../SKILL.md`. Apply it with the active
workspace's own instructions and tracker configuration.

## Audit Method (run before any reorganization)

1. `bd stats`; `bd list --status open --json` (group by type/priority);
   `bd ready`; `bd blocked`; `bd epic status`.
2. **Staleness lives in content, not timestamps.** Bulk touches make every
   `updated_at` identical and useless. Detect rot by reading descriptions:
   - referenced plan/ADR files gone from disk (`ls` each path);
   - ancestor IDs cited as live context but closed (`bd show <id>`);
   - epics with NULL descriptions + hundreds of notes (objective buried in
     note archaeology — synthesize it into the description);
   - same artifact at two filesystem paths (dual-path violation);
   - directives superseded by newer operator law;
   - time-boxed context ("cooperate with N-file lane", stale LOC baselines).
3. Objective mapping: group every open epic under its operator directive. Two
   epics serving one directive = ownership violation → fold weaker into
   stronger as acceptance criteria.
4. Note volume is a signal: thousands of notes = decision archaeology.

## Consolidation Playbook

1. Classify each epic: **drain** (≥70% children closed, ≤2 open) vs **fold**
   (rival/stale container) vs **keep** (unique live objective).
2. Fold: re-parent live children (remove old link first if typed), absorb
   directive as DoD in survivor's description, close with reason naming
   survivor + preserved directive.
3. Rewrite survivor descriptions: current operator laws, absorbed DoDs,
   re-measured baselines (re-run the measurement, never carry stale numbers),
   dependency chain, boundary with sibling epics (which concerns live where).
4. Hygiene in the same pass:
   - `in_progress` AND dep-blocked → choose one truth;
   - stale `blocked` status or block on closed issue → open / remove dep;
   - artificial parent-child-only "blocked" → review and open;
   - cross-repo blocker moved away → append note on the dependent recording
     where the blocker now lives (cross-DB blocks do not exist).
5. Sequence as waves (template):
   - W0 tracker hygiene + consolidation;
   - W1 open P0 incidents, then drains;
   - W2 bottleneck nodes (single beads blocking whole chains);
   - W3 the cascades those bottlenecks release;
   - W4 folds, exports, final production-readiness gate.

## Cross-DB Migration

```bash
install -d -m 700 "${XDG_STATE_HOME:-$HOME/.local/state}/beads/migrations"
bd export | jq -c 'select(.id as $i | ["id-1","id-2"] | index($i)) | del(.dependencies)' > "${XDG_STATE_HOME:-$HOME/.local/state}/beads/migrations/move.jsonl"
bd -C /path/to/target-repo import - < "${XDG_STATE_HOME:-$HOME/.local/state}/beads/migrations/move.jsonl"   # upsert; IDs + notes preserved
```

Strip `dependencies` (local links dangle in the target DB). Close in source
with reason `MOVED to <db path> (same ID)`; re-wire surviving intra-set blocks
on the target side; note cross-repo blockers on dependents left behind.

## Verification (after every mutation batch)

`bd stats` + `bd epic status` + `bd blocked` + `bd ready`:

- ready queue opens with the Wave-1 P0s;
- blocked count reflects only real open blockers;
- no epic without description; no in_progress without a live owner;
- then, and only then, `bd github sync` (organize-before-first-sync law;
  drift afterward is a defect to fix immediately, never a second truth).

## Merge-Gate Sizing (UNIVERSAL_CORE 13)

Prefer short validated lanes that merge fast: one bead = one reviewable PR,
green within a session. At review time, reject (return for split) any lane
too big to validate in one pass; a lane that cannot merge green within a
session is a defect to split, not to nurse. Verify the lane updated the docs
its change affects — missing doc updates are a review blocker.
