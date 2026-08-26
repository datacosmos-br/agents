---
name: doc-drift
description: "Execute documentation-drift fixes across town and rigs. USE FOR: acting on a governance-audit finding or an explicit operator flag (--auto-fix); conventions check, extinct-flag grep, live-reference validation. DO NOT USE FOR: deciding what counts as drift (governance-audit recommends; this skill executes); editing generated projections by hand."
license: MIT
metadata:
  bundle: docs
  scope: universal
---

# Doc Drift — Executor

Runs only on a `governance-audit` finding reference or explicit operator request.

## Steps

1. **Conventions**: `bd doctor --check=conventions && bd lint`.
2. **Extinct flags/contracts**: grep `docs/`, skills, AGENTS.md for flags, APIs, or contracts current code no longer supports. Acceptable only in extinction notes.
3. **Live references**: verify every cited command, script, helper, symbol exists in the runtime; update stale references in place.
4. **Auto-fix** (`--auto-fix` only): `gt doctor --fix`; normalize command frontmatter to canonical bodies; align `.gitignore` patterns across rigs to canonical set.
5. **Evidence**: record commands, outputs, fixes applied on the audit bead (or a new bead in the owning context: town → `hq-*`, rig → `<prefix>-*`). Commit changes.

## Critical rules

- No finding, no run — recommendations come from `governance-audit`, execution lives here.
- Fix sources, never hand-edit generated projections; regenerate instead.
