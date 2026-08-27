# Gas City execution law

Gas City 1.4.1 is the orchestration contract. Active guidance uses its native
primitives: city, rig, Pack V2, agent, formula, run, session, order, and event.

## Configuration

- `city.toml` declares the city, providers, rigs, agents, and rig imports.
- Reusable behavior is a Pack V2 (`schema = 2`) with explicit pinned imports
  and a committed lock. Materialized files are generated output, not owners.
- A rig registers a project. Agents are persistent configured workers. Formulas
  define work graphs; runs and sessions provide operational evidence.

## Workflow

1. Resolve configuration and validate it before dispatch.
2. Select an existing rig, declared agent, and formula.
3. Dispatch with `gc sling <agent> <work> --on <formula>` only when runtime is
   authorized and healthy.
4. Inspect run and session state; never infer completion from process exit alone.
5. Land through the repository's native gates and PR integration contract.

## Prohibitions

- No active Gas Town command, role hierarchy, compatibility pack, or fallback.
- No mechanical `gt` to `gc` translation; `gc done` and `gc commit` do not exist.
- No Pack V1, implicit import, generated-file edit, symlink, or cross-repo path.
- Gas City-specific skills are personal governance and never project projections.
- Until runtime suspension is lifted, no `gc init`, `gc start`, dispatch, Beads,
  or Dolt operation is permitted.
