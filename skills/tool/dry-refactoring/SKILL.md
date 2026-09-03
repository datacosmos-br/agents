---
name: dry-refactoring
description: 'jscpd clones, copy-paste duplication, extract function, refactoring workflow'
allowed-tools: 'Bash(npx *)'
metadata:
  aihub.tags: '["activation:opt-in","decision:plan-00","detect:opt-in:dry-refactoring","effective:2026-09-03","provenance:agents-owned","route:agent","route:project","tool:dry-refactoring","updates:manual","usage:on-demand"]'
  version: 1.1.0
---

# dry-refactoring

Guided workflow to eliminate copy-paste duplication detected by jscpd.

## Detect clones

```bash
npx jscpd --min-lines 8 --mode strict --reporters ai --summary <path>
npx jscpd --baseline <path>/.jscpd-baseline.json --fail-on-new-clones 0 \
  --min-lines 8 --mode strict --reporters ai <path>
```

Eight lines is the comparison floor. A selected project config may replace the
flags only by declaring the same threshold and baseline explicitly. A baseline
is regression control, not permission for semantic debt: retriage it whenever
threshold, configuration, or reviewed files change.

## Workflow

1. Resolve the writable worktree, integration base, project gate owner, and
   baseline. For another repository, snapshot its committed integration ref —
   including each recorded submodule commit — instead of scanning dirty state.
2. Parse each clone line into its two locations (file + line range).
3. Read both fragments; classify semantic duplication, canonical projection,
   generated/historical evidence, distinct fixture, or tokenizer false
   positive. Textual similarity alone authorizes no edit.
4. Remediate only confirmed semantic duplication (strategies:
   `references/procedure.md`).
5. Rebaseline only after triage, then require zero new clones. Record command,
   working directory, exit code, before/after counts, and disposition.

Cross-format clones (`.js`/`.ts`, via `--cross-formats`) usually mean code was
ported without deleting the original: consolidate into one implementation and
update imports rather than extracting a third copy. A clone between test
files may indicate a missing test helper; across unrelated modules, a missing
shared utility.
