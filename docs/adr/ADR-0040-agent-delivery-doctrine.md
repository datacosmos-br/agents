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
5. A phase runs the delivered behavior in runtime first, then `make fix`, `make fmt`,
   `make check` and `make tests` — never the reverse — and ends only with its PR
   merged into the integration branch and the delivered behavior proven in runtime
   again on the integrated revision.
6. Another agent's work is adopted with `git cherry-pick`; never reset, stash, rebase,
   discard or force-push it, and never open a second lane for the same work.
7. One owner per value, file and surface; a copy is a defect.
8. The environment and the upstream are never guilty: every host, toolchain, environment
   and upstream library, class or method behaves as declared, so a failure belongs to the
   consumer — its call, version, declaration or assumption — and is repaired at that
   consumer's owner. When that owner is an upstream we own, the upstream is fixed; when it
   is not, the call is corrected to the upstream's contract instead of a local wrapper,
   shim, patch or fallback. Only a proven environment failure stops the work: the exact
   command, revision, exit and decisive output, plus proof that the same input succeeds
   where the environment is intact. With that proof the agent stops, reports the evidence
   to the operator, and neither works around, recreates nor masks the environment.

## Consequences

- A tree whose `gen` does not pass is not committable.
- An unmerged PR is not a finished phase; a merged PR without runtime proof is not a
  finished phase either.
- Environment and supplier explanations are refused: the repair is always in the
  change the agent made, or in the upstream owner we hold.
- A genuine environment failure is honored only with its proof, and is reported rather
  than repaired by a second local layer.

## Amendment 2026-11-24

The operator decided on 2026-11-25 that the cycle of FLEXT #2791 prevails: `make check`
is the only gate, followed by the runtime proof and the project's test verb last; `gen`,
`fix` and `fmt` are no longer separate cycle steps, and adoption is by
`git cherry-pick -x`. Decision 5 and the first consequence above are superseded by
[the delivery cycle](../../rules/workflow/agent-delivery-doctrine.md#the-delivery-cycle).

## Amendment 2026-11-27

The operator ordered on 2026-11-27 the new `make check` standard everywhere: FLEXT
ADR-037 (flext-infra #2791) makes `make check` the single gate that generates, repairs
lint and formats to a fixed point before validating. This repository retires its own
`gen`, `fix` and `fmt` verbs into `make check`; ADR-0041 is superseded on that point.
