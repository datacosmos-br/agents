---
metadata:
  aihub.tags: '["route:personal"]'
---

# Gas City static boundary

The project-selected, pinned Gas City release is the orchestration contract.
Active guidance uses its native primitives: city, rig, Pack V2, agent, formula,
run, session, order, and event. Installation never selects orchestration. An
unselected installation adds no command, hook, tracker, workspace, or gate.
Runtime is suspended here, so this file authorizes static configuration review
only.

## Configuration

- `city.toml` declares the city, providers, rigs, agents, and rig imports.
- Reusable behavior is a Pack V2 (`schema = 2`) with explicit pinned imports
  and a committed lock. Materialized files are generated output, not owners.
- A rig registers a project. Agents are persistent configured workers. Formulas
  define work graphs; runs and sessions provide operational evidence when the
  runtime is explicitly restored.
- A selected Gas City workflow uses its explicitly declared store. If the
  project also selects Beads, Beads owns durable tracking and closure. A Gas
  City workflow without Beads has no Beads command, hook, issue, or gate.

## Repository boundary during suspension

- Work only in the existing authorized checkout.
- Repository Git, native gates, PR review, and merge-commit landing remain local
  responsibilities.
- Create no city, rig, Pack, agent, formula, run, session, clone, worktree,
  workspace, symlink, cross-repository reference, tracker, or alternate ledger.
  Preserve evidence only in separately authorized Git/PR/CI surfaces.
- Static Gas City skills are personal governance and never project projections.

## Prohibitions

- No active Gas Town command, role hierarchy, compatibility pack, or fallback.
- No mechanical old/new command translation or compatibility command.
- No Pack V1, implicit import, generated-file edit, symlink, or cross-repo path.
- Once selected and restored, validate the whole declared city, rig, Pack,
  provider, store, workspace, authority, and host readiness before effects. The
  first defect stops that workflow without retry, alternate store, fallback, or
  direct-mode degradation.
- Until runtime suspension is explicitly lifted, every orchestration, tracker,
  and database operation is prohibited.
