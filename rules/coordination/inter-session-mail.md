---
description:
  Actors coordinate through gc mail and adopt open or idle work instead of redoing it.
metadata:
  aihub.tags: '["decision:ADR-0038","effective:2026-11-03","route:personal"]'
---

# Coordination through gc mail

Where Gas City is selected, actors coordinate through `gc mail` (skill `gc-mail`) under
its active coordinator; without a channel, decisions and blockers are recorded on the
owning bead for the operator. Decisions, handoffs and blockers go to mail and the bead,
an operator's order is relayed in the operator's own words, and an operator-authorized
direct channel counts once repeated in mail. Before the first effect, read mail, adopt
open work on the same scope instead of redoing it, and declare bead, branch and PR.
Overlapping work and shared-infrastructure changes are announced first and continue.
A dispute between actors is settled by the active coordinator (the Gas City mayor) by
priority, age and alignment with the approved plan, and then by the operator; its
discussion and agreement are recorded in the mail thread and on the bead, automatically
wherever Gas City and Beads are selected. Work idle past
`coordination.abandonment_threshold_minutes` (`config/governance.json`) is open to
adoption, never to deletion or closure ([law](../law.md) 11).
