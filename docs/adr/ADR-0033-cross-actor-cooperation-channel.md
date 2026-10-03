# ADR-0033 — Cross-actor cooperation through gc mail and the operator relay

- **Status:** Accepted
- **Date:** 2026-10-03
- **Tracking:** bead `gc-13572e` (DotGasCity hardening cutover); operator directive 2026-10-03

## Context

Multiple executor families work the same fleet concurrently: interactive coding
sessions (zcode, kilo, codex, claude — and any future provider), Gas City agent
sessions (mayor, dispatcher, witness, refinery, polecat, dogs), and the Hermes
assistant that bridges to the operator's WhatsApp. During the 2026-10-02/03
city reactivation, two campaigns worked overlapping scopes without a mailed
agreement, and the operator had to intervene: "use gc mail, make agreements,
execute synergistically, fix forward, adopt". The requirement is not limited
to agent sessions and does not depend on how many executors exist.

## Decision

1. **One coordination channel for all actors.** Every actor working an
   operator-authorized objective — whatever provider or surface it runs on —
   coordinates through `gc mail`. Before touching a shared target, read the
   mailbox and the tracker for an active agreement; declare your lane
   (bead + branch + PR) to the coordinating tier (active mayor/supervisor, or
   the human) before the first effect.
2. **Agreement before overlap; adopt over rework.** Two actors whose scopes
   intersect either agree on ownership through mailed, bead-recorded terms or
   one yields. Whoever arrives second adopts the surviving lane
   (fix-forward/adopt); silent duplication is a violation, not bad luck.
3. **The relay is part of the law, not an extra.** Hermes is a bound actor:
   operator-facing questions and confirmations may travel the
   Gas City → Hermes → WhatsApp path, and answers land back as evidence on
   the owning bead (gc mail or transcript). A channel that cannot carry
   evidence is a notification nicety, never the record.
4. **Actor identity never changes the law.** The rule binds zcode, kilo,
   every current provider, and any future one equally; "my executor is
   different" is not a variance.

## Consequences

- Executor sessions must resolve the coordinating tier at startup the same
  way they resolve tracker activation — by reading, not assuming.
- Governance delivery (capsules, projections) carries this rule to every
  provider surface; the Hermes bridge contract references it instead of
  redefining coordination.
