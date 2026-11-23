# ADR-0040 - Agent delivery doctrine

**Status:** Accepted **Date:** 2026-11-23 **Scope:** every rule, skill, command and
session, in every project

## Authority

Operator order, 2026-11-23 (session OpenMoat/OpenCode): a red is always the agent's
own and never the environment or the supplier toolchain; the integration tip is the
only base; native verbs run the work and are never bypassed; agent surfaces are
published only by AI Hub; a phase ends with its PR merged **and** its behavior proven
in runtime; another agent's work is adopted by `git cherry-pick`; `--no-verify` is
never used.

## Context

Measured in one session on 2026-11-23, in this order: `make gen` refused by gate
admission because no green `check` preceded it; two `pydantic-census` projection
drifts; a `portable-home` failure from an absolute home path in an example; a stale
workspace ledger that refused `workspace-config`; a V1 plugin entry that OpenCode 2
never loads; and a repository policy that denied the documented light gate
(`ruff check <path>`, `pyrefly check <path>`, a targeted `pytest`, `uv run`,
`mise trust`, `cargo`). Each was first explained as the environment or the supplier,
and each was in the change the agent had made. The cycle also stalled twice at the
merge step: a draft PR whose CI was skipped, and a projection the agent could not
write by hand.

## Decision

`rules/workflow/agent-delivery-doctrine.md` is the binding rule:

1. Every red is the agent's; repair it at its owner before writing again.
2. The integration tip is the only base; merge it `--no-ff` before the commit and
   again before finishing, and revalidate on the integrated revision.
3. Native verbs run the work; never bypass one, never add a second path beside it,
   never `--no-verify`.
4. Agent surfaces (configuration, hooks, MCP, skills, policy) are published by AI Hub
   from declarations; a manual edit or a manual agent command is a defect.
5. A phase ends only with its PR merged into the integration branch and the delivered
   behavior proven in runtime.
6. Another agent's work is adopted with `git cherry-pick`; never reset, stash, rebase,
   discard or force-push it, and never open a second lane for the same work.
7. One owner per value, file and surface; a copy is a defect.

## Consequences

- A tree whose `gen` does not pass is not committable.
- An unmerged PR is not a finished phase; a merged PR without runtime proof is not a
  finished phase either.
- Environment and supplier explanations are refused: the repair is always in the
  change the agent made.
