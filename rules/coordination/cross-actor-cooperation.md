---
description: Every actor — executor session, Gas City agent, or Hermes relay — coordinates through gc mail, agrees before overlap, and adopts over rework.
metadata:
  aihub.tags: '["decision:ADR-0033","effective:2026-10-03","route:both"]'
---

# Cross-actor cooperation runs through gc mail

All actors working an operator-authorized objective coordinate through
`gc mail`, whatever executes them: interactive coding sessions (zcode, kilo,
codex, claude, future providers), Gas City agent sessions, or the Hermes
assistant relaying to the operator's WhatsApp.

## Duties

1. **Read before you write.** At startup, resolve the coordinating tier
   (active mayor/supervisor tier, else the human) and scan the mailbox and
   the tracker for agreements touching your scope.
2. **Declare your lane.** Bead + branch + PR, mailed to the coordinating
   tier before the first effect — the same birth certificate
   `lane-ownership-declaration` requires, extended to every executor family.
3. **Agree before overlap.** Intersecting scopes need a mailed,
   bead-recorded ownership agreement; arriving second means adopting the
   surviving lane (fix-forward/adopt), never duplicating it.
4. **Relay carries questions, bead carries evidence.** Operator-facing
   confirmations may travel Hermes → WhatsApp; the answer lands back on the
   owning bead. A channel that cannot carry evidence is never the record.
5. **Identity never waives the law.** Provider, session kind, or "my
   executor is special" changes nothing in this rule.

## Boundaries

- Channel mechanics (endpoints, injection, delivery proof) remain owned by
  `inter-session-mail` and the Gas City boundary (`gascity.md`).
- Operator precedence (`operator-precedence.md`) still wins over any
  in-flight agreement.
