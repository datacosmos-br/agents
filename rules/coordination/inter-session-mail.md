---
description: Every running session talks to every other session only through gc mail.
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-09-19","route:personal"]'
---

# Inter-session communication goes through gc mail

Sessions that share a machine, a repository, or a lane talk to each other only
through `gc mail`, the city's bead-backed mail. Chat relays, notes left in a
working tree, comments in product files, and conclusions drawn from process state
are not communication. Mail is the record of what was said; the owning rig's bead
is the ledger of what was decided. A provider's direct cross-session channel is a
fast path only: every message sent through it is repeated in the gc mail thread,
which stays the record.

The `gc-mail` skill owns the complete contract:
- city-store selection and addressing;
- the five delivery receipts;
- presence and liveness, including that a missing reply is never absence;
- the city hall campaign thread;
- the subject taxonomy;
- the authority table.

It is declared there once, because the skill is the artifact that every provider
home receives; this rule declares only the obligation.

A decision, a handoff, and a blocker go to mail and to the owning rig's bead; one
without the other is not a record.

Abandonment, adoption, and their limits are declared once, in
`bead-branch-pr-cadence` (rule file) §2. The adopter announces `[coord] lane claim`
before the first effect. Two actors on one working tree is itself a blocker:
declare it by mail before the next edit, and agree on one executor.

Compose with `fix-forward collaboration` (rule file), `multiagent edit breadcrumb`
(rule file), `coordinator-ladder` (rule file), and `operator precedence` (rule file).
