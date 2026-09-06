# ADR-0007 — Hook delivery belongs to the runtime the hook executes

- **Status:** Accepted
- **Date:** 2026-09-06
- **Scope:** Provider lifecycle hooks, projection surfaces, capsule delivery
- **Relates to:** ADR-0003, ADR-0004
- **Supersedes:** The lifecycle-hook delivery contract of ADR-0005; every other
  decision in ADR-0005 (composition owner, static instructions, selection,
  capability intersection) stands unchanged

## Context

ADR-0005 gave `agentsctl sync` both halves of governance delivery: it renders
the capsule *and* writes the provider lifecycle hook that injects it, across
seven providers and both scopes — fourteen declared cells.

Two facts made that untenable.

**A hook is not a document; it is an invocation.** Every hook this owner wrote
was `python3 <absolute path>` naming a script under the destination's own
`aihub-hooks/` directory. In personal scope that path derives from `${HOME}` and
is portable. In project scope it is one machine's absolute path committed into a
portable repository, where it is dead on every other host. A measured sweep
found 274 provider hook configs and 768 wrapper scripts across 46 checkouts,
1,244 of those files tracked in git — none referencing a portable entry point.

**Two owners were writing one file.** The runtime whose entry point actually
serves these boundaries — ai-hub — also writes the same provider configuration
files, for the same events, in the agent's own home. On the measured host,
`~/.cursor/hooks.json` carried ai-hub's commands while
`~/.cursor/.hooks.json.agents-governance.json` claimed the same file and the
same events for this owner. Last writer won, and the capsule stopped being
delivered at `sessionStart`. Each side's deploy removed what the other wrote, so
neither could end it alone. `rules/coordination/session-governance.md` already
forbids exactly this: a hook is "never a policy owner, public command, fallback,
daemon, or **second runtime path**."

## Decision

Content and delivery have separate owners, and neither writes the other's
surface.

**`agentsctl sync` owns content.** Skills, commands, rules, and the one
canonical governance capsule rendered from them
(`instruction_projection.capsule`). It publishes that capsule into the providers
whose rules surface is a document — `AGENTS.md`, `GEMINI.md` — through a managed
region that preserves foreign text and rejects edits to owned content.

**The executed runtime owns hook delivery.** A hook that names an interpreter
and a script is alive only where that runtime is installed, so its deploy is the
only owner that can keep the command correct, and it projects only into the
agent's own home — never into a project or workspace.

`hooks` is therefore removed as a projection surface. `config/projections.json`
declares four surfaces (skills, commands, agents, rules) over seven providers and
two contexts: 56 cells, schema `version: 7`, with the hook manifest version
retired. `ProjectionSurface.HOOKS`, `HookEvent`, `HookCoverage`, `HookClient`,
the native-event validation, the wrapper-script emitters, the per-provider config
mergers and the hook manifest reader/writer are deleted, not deprecated.
`hook_projection.py` becomes `instruction_projection.py`: the document-layout
rules projection it always also owned, now named for what it is.

The capsule keeps exactly one builder. It is public so the runtime that owns
hook delivery renders from it instead of reimplementing it.

## Consequences

- The capsule reaches a session through two deliveries with one source: this
  owner's document merge, and the executed runtime's hook.
- A project checkout receives no hook artifact from this owner, so no portable
  repository acquires a host-specific interpreter path from a projection.
- Existing project-scope hook artifacts across the fleet become historical
  residue: this owner writes no new one, and each is removed at its own
  repository, adjudicated against the `owner` field of its sibling manifest.
- ADR-0005's lifecycle coverage table and its provider hook references are
  historical evidence for a contract this owner no longer holds. The runtime
  that now owns delivery states its own coverage.
- A future provider surface that merely *stores* text stays here. One that
  *executes* a command belongs to whichever runtime that command starts.
