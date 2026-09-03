---
description: Bead verification is critical and mandatory
metadata:
  aihub.tags: '["decision:ADR-0007","effective:2026-08-30","route:both"]'
---

# Bead verification is critical and mandatory

At creation, update and close, every bead passes four independent sources:

1. **Registered state** — authorized documents, handoffs and receipts; correct
   contradictions at their ledger owner.
2. **Git history** — commits and merged PRs on the integration lane.
3. **Measured reality** — disk, processes and endpoints, with command, working
   directory, exit code and decisive output.
4. **Current-code intent** — integrated HEAD, never an older revision. Close a
   retired premise as obsolete with evidence; never execute it as written.

The bead is the hypothesis; reality is proof. Closing without four-source
evidence is a violation. Fix divergence in the bead, never in reality.

Each managed execution uses one HQ root and linked bead per rig, both carrying
four-source checkpoints. Instructions, tracker prime, and skills enforce this;
divergence, parallel roots, and mail ledgers fail.
