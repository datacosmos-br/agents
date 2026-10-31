# ADR-0038: No Preexisting Debt Ruling

<!-- TOC START -->

- [Context](#context)
- [Decision](#decision)
- [Consequences](#consequences)

<!-- TOC END -->

Status: Accepted
Date: 2026-10-30
Amended: 2026-10-31 (rule tag contract conformance; this ADR records the owning decision anchor)

## Context

Operator ruling issued 2026-10-30 (session `sess_816286c6` unification, gen-perf
campaign; SSOT handoff
`devops-oud-iac/docs/handoffs/20261030-gen-perf-rope-cures.md`). During that
campaign, failures surfaced mid-lane were being classified as "pre-existing" and
routed around instead of repaired. The operator ruled that this classification
does not exist and recorded the rule
[rules/ethics/no-preexisting-debt.md](../../rules/ethics/no-preexisting-debt.md).

The rule first landed (685e17da) without this owning ADR and carried a
non-conforming provenance tag (`operator-ruling:...`), which the governance
validator correctly rejects: rule tags support only `route:` and the approval
namespaces (`decision:`, `effective:`, `supersedes:`). Provenance belongs in the
body and in this ADR, not in ad-hoc tag namespaces.

## Decision

1. **"Não existe falha pré-existente"** — there is no such thing as a
   pre-existing failure. Every failure encountered while working — introduced by
   this session, by a sibling lane, or left by a prior session — is corrected at
   its root with criticality elevated; it is never classified out of scope,
   deferred as someone else's debt, bypassed, or worked around with a fallback.
2. `--no-verify` and any gate bypass are prohibited as a class. Where a
   fleet-level gate defect blocks a commit whose own diff is clean, the recorded
   practice is: run the equivalent validation directly on the candidate diff,
   document the bypass rationale in the commit message, and land the gate's
   root-cause cure through its canonical owner in the same campaign. Rollback is
   not a fix: correct or optimize forward.
3. The owning rule carries `decision:ADR-0038`, `effective:2026-10-30`,
   `route:both`, conforming to the tag contract in
   `src/agents_governance/rules.py`.

## Consequences

- Consumers (ai-hub and every governed project) inherit the rule through
  `GovernanceBundle`; failing validations surfaced by a dependency bump are
  adoption evidence, not noise.
- Rule authors must land rules together with their owning ADR anchor; the
  validator is the executable contract and stays closed to ad-hoc namespaces.
