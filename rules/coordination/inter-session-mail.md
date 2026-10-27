---
description: gc mail is the only record of communication between running sessions.
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-09-19","route:personal"]'
---

# Inter-session communication goes through gc mail

Sessions that share a machine, a repository, or a lane coordinate only through
`gc mail`, the city's bead-backed mail. Chat relays, notes left in a working tree,
comments in product files, and conclusions drawn from process state are not
communication. Mail is the record of what was said; the owning rig's bead is the
ledger of what was decided.

A provider's direct cross-session channel exists only where the operator authorized
it. Today that is Claude↔Claude, per tracker memory
`operator-ruling-2026-10-09-session-channel-sendmessage`. It is a fast path: a
message sent through it counts only once it is repeated in the gc mail thread, which
stays the record.

The `gc-mail` skill supplies the native procedure:

- city-store selection and addressing;
- the five delivery receipts;
- presence and liveness, including that a missing reply is never absence;
- the city hall campaign thread;
- the subject taxonomy;
- the authority table.

The rule owns the coordination obligation and the skill owns that procedure.
Provider delivery and activation are verified by their publication owner;
historical observations about which provider received which file are not
standing evidence of the current installed surface.

Delivery of that opt-in skill to each provider home is ai-hub's (`distribution
routing` (rule file), law 2). A session without it follows the protocol city hall
posts in the campaign thread.

A decision, a handoff, and a blocker go to mail and to the owning rig's bead; one
without the other is not a record.

Abandonment, adoption, and their limits are declared once, in
`bead-branch-pr-cadence` (rule file) §2. The adopter announces `[coord] lane claim`
before the first effect. Shared worktrees follow
[fix-forward collaboration](fix-forward-collaboration.md): coordinate bounded owners
and serialize overlapping mutations, without requiring an exclusive writer or a
clean, frozen checkout.

Compose with `fix-forward collaboration` (rule file), `multiagent edit breadcrumb`
(rule file), `coordinator-ladder` (rule file), and `operator precedence` (rule file).
