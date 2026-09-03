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

## Provenance before conclusion

Before labeling silent or changed state as a defect, trace its actor, time,
and originating PR: `events.jsonl`, file mtimes, `git log -S` on the changed
value, and merged PRs in the window across every registered rig, not just the
one that surfaced the change. A state without a proven author is neither
defect nor intention — it is unproven, and stays unproven until one of the
four sources names an actor and a time. A rig's config changed by a merged
cross-repo cutover PR is provenance, not silence; correct the bead's premise
instead of opening a defect against the receiving rig.
