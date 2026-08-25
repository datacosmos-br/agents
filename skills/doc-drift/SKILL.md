---
name: doc-drift
description: >-
  Detect and fix documentation drift across town and all rigs.
  Runs conventions check, extinct-flag grep, live-reference validation,
  auto-fix via gt doctor --fix, and creates evidence bead.
allowed-tools: "Bash(gt *), Bash(bd *), Bash(git *)"
version: "1.0.0"
author: "Gas Town"
---

# Doc Drift — Continuous Standardization

Usage: /doc-drift [--rig <name>] [--auto-fix]

Arguments: $ARGUMENTS

## Step 1: Conventions check

Run beads conventions and lint:

```bash
bd doctor --check=conventions
bd lint
```

If `--auto-fix` is set, run `gt doctor --fix` and re-run conventions until clean.

## Step 2: Extinct flags/contracts

Grep `docs/`, `.claude/`, `skills/`, and `AGENTS.md` for flags, APIs, or
contracts the current code no longer supports. Acceptable only in extinction
notes or gate definitions.

## Step 3: Live references

Verify every command, script, helper, and symbol cited in docs/skills actually
exists in the current runtime. Update stale references in place.

## Step 4: Auto-fix (only with --auto-fix)

Canonical fixes:

- `gt doctor --fix` — config, beads, hooks, gitignore
- Normalize `.claude/commands/` frontmatter to canonical bodies
- Archive stale `.omo/plans/` and `.omo/drafts/` to `.omo/archive/`
- Align `.gitignore` patterns across rigs to canonical set

## Step 5: Evidence and bead

Create a bead in the owning context:

- town root → `hq-*`
- rig root → `<prefix>-*`

Record command, output, and fixes applied. Commit changes and close the bead.
