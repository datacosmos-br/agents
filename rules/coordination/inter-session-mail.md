---
description:
  Actors align before each plan's first effect and adopt open or idle work.
metadata:
  aihub.tags: '["decision:ADR-0038","effective:2026-11-03","route:personal"]'
---

# Coordination between actors

Every plan starts by aligning with the actors on its scope: Claude sessions through
their native session messaging, every other actor through `gc mail` (skill `gc-mail`)
under its active coordinator (`operator-order-2026-11-21-do-it-align-ccd-gc-mail`);
without a channel, decisions and blockers go on the owning bead. Decisions, handoffs
and blockers go to that channel and the bead, an operator's order is relayed in the
operator's own words, and a direct channel counts once repeated in mail. Read the
channel, adopt open work on the same scope instead of redoing it, and declare bead,
branch and PR.
Overlapping work and shared-infrastructure changes are announced first and continue.
A dispute between actors is settled by the active coordinator (the Gas City mayor) by
priority, age and alignment with the approved plan, and then by the operator; its
discussion and agreement are recorded in the mail thread and on the bead, automatically
wherever Gas City and Beads are selected. Another lane is never a reason to wait: work a
plan needs that stalls there is messaged once on its channel, then adopted, finished and
landed by the actor that needs it (`operator-order-2026-11-21-no-lane-excuse`); a stopped
or unreachable owner's lane is adopted the same way, its bead claimed before the first
effect, and two writers never share one lane (`operator-order-2026-11-21-done-no-excuses`). Other work
idle past
`coordination.abandonment_threshold_minutes` (`config/governance.json`) is open to
adoption, never to deletion or closure ([law](../law.md) 11).
