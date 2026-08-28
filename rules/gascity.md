# Gas City static boundary

Gas City 1.4.1 is the orchestration contract. Active guidance uses its native
primitives: city, rig, Pack V2, agent, formula, run, session, order, and event.
Its runtime is suspended. This file documents configuration ownership only and
authorizes no initialization, start, dispatch, inspection, repair, tracker, or
database operation.

## Configuration

- `city.toml` declares the city, providers, rigs, agents, and rig imports.
- Reusable behavior is a Pack V2 (`schema = 2`) with explicit pinned imports
  and a committed lock. Materialized files are generated output, not owners.
- A rig registers a project. Agents are persistent configured workers. Formulas
  define work graphs; runs and sessions provide operational evidence when the
  runtime is explicitly restored.

## Repository boundary during suspension

- Work only in the existing authorized checkout.
- Repository Git, native gates, PR review, and merge-commit landing remain local
  responsibilities.
- Create no city, rig, Pack, agent, formula, run, session, clone, worktree,
  workspace, symlink, cross-repository reference, tracker item, or substitute
  ledger.
- Static Gas City skills are personal governance and never project projections.

## Prohibitions

- No active Gas Town command, role hierarchy, compatibility pack, or fallback.
- No mechanical old/new command translation or compatibility command.
- No Pack V1, implicit import, generated-file edit, symlink, or cross-repo path.
- Until runtime suspension is explicitly lifted, every orchestration, tracker,
  and database operation is prohibited.
