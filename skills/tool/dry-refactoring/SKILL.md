---
name: dry-refactoring
description: 'jscpd clones, copy-paste duplication, extract function, refactoring workflow'
allowed-tools: 'Bash(npx *)'
metadata:
  aihub.tags: '["activation:opt-in","decision:plan-00","detect:opt-in:dry-refactoring","effective:2026-09-03","provenance:agents-owned","route:agent","route:project","tool:dry-refactoring","updates:manual","usage:on-demand"]'
  version: 1.3.0
---

# dry-refactoring

Guided workflow to eliminate copy-paste duplication detected by jscpd.

## Detect clones

```bash
npx --yes jscpd@5.1.2 --min-lines 8 --mode strict --reporters console \
  --exit-code 1 <path>
```

Eight lines is the comparison floor. A project may change flags only through
its canonical gate and selected executable. Zero reported clones is mandatory;
there is no baseline suppression contract.

## Workflow

1. Resolve the writable worktree, integration base, and gate owner.
2. Parse each clone line into its two locations (file + line range).
3. Read both fragments; classify semantic duplication, canonical projection,
   generated/historical evidence, distinct fixture, or tokenizer false
   positive. Textual similarity alone authorizes no edit.
4. Remediate only confirmed semantic duplication (`references/procedure.md`).
5. Require zero clones, then prove the merged integration commit, command,
   working directory, exit code, before/after counts, and runtime.

Cross-format clones usually mean a port kept both implementations; consolidate
at one owner. Test clones often need a helper; unrelated-module clones often
need a shared utility.

Never infer flags from another version: execute the project gate and verify the
selected jscpd help when its contract is under change.
