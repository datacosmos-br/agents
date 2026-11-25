---
description: AI Hub owns every projection; config has one SSOT; FLEXT consumes nothing from AI Hub
metadata:
  aihub.tags: '["decision:ADR-0038","effective:2026-11-24","route:both"]'
---

# AI Hub ownership

The delivery order, adoption and red ownership are in the
[agent delivery doctrine](agent-delivery-doctrine.md); environment faults in
[law 13](../law.md). This rule adds the ownership facts:

- Never edit a live agent home, a generated projection, OpenMoat policy, the CRG graph
  or the OpenViking store by hand, and never run their commands outside AI Hub. AI Hub
  is the only projector and publisher. The hook owner is the cohort AI Hub currently
  declares (`config/agents.yaml`, AI Hub ADR-0045/0030), never assumed.
- Every config lives in AI Hub `config/` under its owning domain (workspaces, agents,
  tools, mcp, models, services) with one SSOT; a project adjusts only through its
  override, and a worktree inherits its workspace's permissions. Never duplicate or keep
  an unused declaration.
- FLEXT projects consume no AI Hub configuration (FLEXT ADR-036); a host tool such as
  Cubic enters through the existing verbs, gated by a credential AI Hub delivers.
- Always use the newest FLEXT from the integration branch.
- Align with every other session before and during the work through the declared
  coordination channel (gc mail; the owning Bead when it is unavailable), sharing the
  exact commit and branch so either side cherry-picks instead of duplicating. An
  OpenMoat defect is raised with the OpenMoat session there.
