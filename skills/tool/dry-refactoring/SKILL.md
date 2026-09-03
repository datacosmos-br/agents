---
name: dry-refactoring
description: 'jscpd clones, copy-paste duplication, extract function, refactoring workflow'
allowed-tools: 'Bash(npx *)'
metadata:
  aihub.tags: '["activation:opt-in","decision:plan-00","detect:opt-in:dry-refactoring","effective:2026-09-03","provenance:agents-owned","route:agent","route:project","tool:dry-refactoring","updates:manual","usage:on-demand"]'
  version: 1.2.0
---

# dry-refactoring

Guided workflow to eliminate copy-paste duplication detected by jscpd.

## Detect clones

```bash
npx --yes jscpd@5.1.2 --min-lines 8 --mode strict --reporters ai --summary <path>
npx --yes jscpd@5.1.2 --baseline <path>/.jscpd-baseline.json --fail-on-new-clones 0 \
  --min-lines 8 --mode strict --reporters ai <path>
```

Eight lines is the comparison floor. A project may change flags only by
declaring the same threshold and committed baseline explicitly. A baseline is
regression control, not permission for semantic debt.

## Workflow

1. Resolve the writable worktree, integration base, gate owner, and triaged
   baseline; never scan dirty residue as a baseline.
2. Parse each clone line into its two locations (file + line range).
3. Read both fragments; classify semantic duplication, canonical projection,
   generated/historical evidence, distinct fixture, or tokenizer false
   positive. Textual similarity alone authorizes no edit.
4. Remediate only confirmed semantic duplication (`references/procedure.md`).
5. Require zero new clones, then prove the merged integration commit, command,
   working directory, exit code, before/after counts, and runtime.

Cross-format clones usually mean a port kept both implementations; consolidate
at one owner. Test clones often need a helper; unrelated-module clones often
need a shared utility.

JSCPD v4 has no baseline contract; never let an unpinned `jscpd` command
select it.
