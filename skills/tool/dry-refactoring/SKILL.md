---
name: dry-refactoring
description: 'jscpd clones, copy-paste duplication, extract function, refactoring workflow'
allowed-tools: 'Bash(npx *)'
metadata:
  aihub.tags: '["activation:opt-in","decision:plan-00","detect:opt-in:dry-refactoring","effective:2026-08-28","provenance:agents-owned","route:agent","route:project","tool:dry-refactoring","updates:manual","usage:on-demand"]'
---

# dry-refactoring

Guided workflow to eliminate copy-paste duplication detected by jscpd.

## Detect clones

```bash
npx jscpd --reporters ai <path>                          # clone list
npx jscpd --reporters ai --cross-formats "js-ts" <path>  # clones spanning related formats
npx jscpd --reporters ai --summary <path>                # + per-file dup% hotspots
```

Use `--min-lines 10` to filter noise. On larger codebases, `--summary` lists
top files and folders with a `dup%` column — high `dup%` with high token
counts pays off most.

## Workflow

1. Run jscpd on the target path; pick the highest-impact clone first.
2. Parse each clone line into its two locations (file + line range).
3. Read both fragments; understand what they do.
4. Design the extraction (strategies: `references/procedure.md`).
5. Apply it — update both locations and every other usage.
6. Re-run jscpd to confirm the clone is gone; repeat for remaining clones.

Cross-format clones (`.js`/`.ts`, via `--cross-formats`) usually mean code was
ported without deleting the original: consolidate into one implementation and
update imports rather than extracting a third copy. A clone between test
files may indicate a missing test helper; across unrelated modules, a missing
shared utility.
