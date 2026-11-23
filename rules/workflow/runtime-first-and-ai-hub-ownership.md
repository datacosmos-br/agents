---
description: Runtime first, AI Hub owns every projection, and a red gate is the actor's defect
metadata:
  aihub.tags: '["decision:operator-order-2026-11-23","effective:2026-11-23","route:both"]'
---

# Runtime first and AI Hub ownership

The operator's order of 2026-11-23 binds every agent and session:

- Make the runtime work first: publish through AI Hub and prove the installed runtime;
  only then run `make fix`, `make fmt`, `make check` and `make tests`. Never the
  opposite.
- Never edit a live agent home, a generated projection, OpenMoat policy, the CRG graph
  or the OpenViking store by hand, and never run their commands outside AI Hub. AI Hub
  is the only projector and publisher.
- A failing `make`, `gen`, `check`, `test` or runtime is the actor's own defect, never
  the environment's and never flext-infra's. Repair it at its owner within the FLEXT
  patterns; never bypass, never `--no-verify`, never change a project rule or add a
  make verb without the operator's explicit decision.
- Always use the newest FLEXT from the integration branch.
- Record the change, merge `origin/<integration>` with `--no-ff`, push the lane and its
  PR, and never skip the integration PR merge.
- DONE is merged at the integration tip with the exact-head CI green, review threads
  resolved, and the changed behavior proven in the installed runtime.
- Adopt another lane's work by cherry-pick or a byte-for-byte copy; never overwrite it.
- Assume every environment, upstream library, method and class has no problem: a
  failure is the user's usage until proven otherwise. When it is your responsibility,
  repair it at the owner, including the upstream you own. A genuine environment fault
  requires measured proof: stop and report it, never work around it or blame it.
- Keep every config in its owning domain with one SSOT (workspaces, agents, tools,
  mcp, models, services). Never duplicate a declaration or keep an unused one; a
  project adjusts only through its override.
- Align with every other session before and during the work: gc mail from the city
  root (or the owning Bead when mail is unavailable), and share the exact commit and
  branch so either side cherry-picks instead of duplicating.
