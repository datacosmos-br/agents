# ADR-0014 — rtk is the fleet command and output economy layer

- **Status:** Accepted
- **Date:** 2026-09-07
- **Scope:** Skill routing, capability tags, and the bundle-side contract for
  command/output economy
- **Composes with:** ADR-0008 (GovernanceBundle read-only boundary)

## Context

The fleet adopted rtk (`rtk-ai/rtk`) as its command and output economy layer.
The execution decision — daemon chain rewrite, SSOT-rendered runtime config,
pinned provisioning — belongs to AI Hub and is recorded there
(AI Hub ADR-0029, `docs/adr/0029-rtk-command-output-routing.md`). This
repository owns the reusable governance meaning: how agents are taught to use
rtk, and which capability semantics the bundle publishes.

Shipping the `rtk` skill without a bundle-side decision record left the
capability tags pointing at a document that does not exist here, which the
catalog correctly rejected.

## Decision

The bundle ships `skills/tool/rtk/` with an `evals/rtk/` suite, tagged
`decision:ADR-0014`. The skill teaches: prefer the daemon automatic rewrite
path; use the manual `rtk <command>` prefix only for registry gaps and the
deferred constructs (heredocs, command substitution, file redirects); recover
failures through the referenced tee file; treat filtered failures as failures;
never hand-edit rtk config projections or install a parallel binary; measure
with `gain`/`session`/`discover`; and never bypass canonical Make verbs.

This record carries only routing and behavior semantics. Provisioning,
projections, hook chains, and permissions remain AI Hub decisions per the
ADR-0008 boundary.

## Consequences

- `decision:ADR-0029` tags in bundle skills are invalid here; bundle-side
  authorizations must resolve to this series.
- Future rtk routing changes on the AI Hub side require re-reading this skill
  only when the agent-facing behavior changes.
