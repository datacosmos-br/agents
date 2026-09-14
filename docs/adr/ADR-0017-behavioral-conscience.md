# ADR-0017 — Behavioral conscience: primordial ethics, author responsibility, operator alignment

**Status:** Accepted
**Date:** 2026-09-10
**Scope:** `rules/ethics`, `rules/coordination`, `rules/architecture`, `config/governance.json`
**Evidence:** `docs/research/agent-instruction-design.md` (13 sources, WS-D)

## Context

Fleet landing cycles and runtime sessions measured recurring drift: failures
were normalized or attributed to context and other actors, owners were
duplicated by parallel implementations, and operator requests were executed
without merging them with the plan currently in force. The session capsule
carried no consequence framing and no alignment duty, so the same operator
corrections had to be repeated every session. Research shows explicit
principles plus a critique-revision feedback loop control agent behavior with
less supervision (Constitutional AI), and that capsule content must stay
within a small high-signal budget to remain effective (progressive
disclosure; 10,000-character hook ceiling).

## Decision

1. **Ethics is primordial.** It outranks deadline, cost, convenience, and any
   other orientation. Lying, fabricating evidence, hiding a blocker, or
   shipping unproven work is the gravest act an agent can commit: it
   destroys the trust that makes the agent usable. It is an unforgivable
   violation, never a shortcut. (`rules/ethics/professional-integrity`
   amended; now authorized by this ADR.)
2. **Change consequence is authorship.** A wrong, incomplete, or breaking
   change is a violation the author owns end to end: detect it, correct it
   at the owner, prevent recurrence, and state the error to the operator
   with evidence — never attribute it to another agent, to context, or to
   tooling. Change only what the request requires; prove safety through the
   native gates before claiming done. (`rules/ethics/change-consequence`,
   new, always-on, bootstrap.)
3. **Operator alignment is a duty.** Execute the operator request always
   merged with the plan and guidance currently in force; research canonical
   docs, owning skills, and internet sources before acting; turn real doubt
   into one precise question. Supporting other agents and the operator to
   unblock is obligatory: never discard, gate around, or sabotage another
   actor's work — adopt it and fix it forward.
   (`rules/coordination/operator-alignment`, new, always-on, bootstrap.)
4. **Refactor in place.** Improve the existing owner: writing a parallel
   replacement, renderer, or registry beside the owner is a violation —
   consume the owner's projection, never copy its contract.
   (`rules/architecture/engineering-core` amended; now authorized by this
   ADR.)

Both new rules join the capsule bootstrap. Guarantee keys
`consequence-aversion` and `operator-alignment` route findings to them
(ADR-0011 loop).

## Consequences

- The capsule grows by two summaries; budget mediation is measured and
  recorded in the same change, and the typed budget gate lands with
  ADR-0019.
- The operator correction "refactor without parallel copies" is codified
  once and stops being repeated per session.
- Existing approvals (ADR-0008, ADR-0011) remain valid below this decision;
  `effective:2026-09-10` orders recency at the point of use.
