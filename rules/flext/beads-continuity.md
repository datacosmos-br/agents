---
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-09-10","route:personal"]'
---

# Session continuity for bead governance

At session start in a Beads-managed FLEXT rig, load current execution state with
`bd prime` through the repository-declared environment, then inspect and claim the
active Bead before effects. The `session governance`, `Gas City`, and
`beads verification` rules own context restoration, activation, and evidence; this rule
adds only the FLEXT routing order:

`inviolable rules → make-check → flext-context-routing → branch-matched flext-law → verification-loop`.

Do not run a second batch tracker, stamp speculative evidence, or copy Bead state into a
local plan.
