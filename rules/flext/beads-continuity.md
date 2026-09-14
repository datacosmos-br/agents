---
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-09-10","route:personal"]'
---

# Session continuity for bead governance

At the start of a session in a beads-managed workspace:

1. Run the wip-beads batch processor in dry-run to stamp fresh workspace
   evidence (`scripts/wip-beads.sh --mode collect --limits 25` from the
   `wip-beads` skill bundle); apply only when a bead write is requested.
2. Reconcile skills: this rule pairs with the `wip-beads` skill
   (`skills/tool/wip-beads`), which owns the processor script.
3. Session-router order remains authoritative (session-router.md): inviolable
   rules -> make-check -> flext-context-routing -> flext-law domain delta ->
   verification-loop at completion.
