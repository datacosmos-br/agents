---
description: Beads records execution state only where explicitly selected
metadata:
  aihub.tags: '["decision:ADR-0038","effective:2026-11-03","route:personal"]'
---

# Beads traceability

Only an explicit project or operator selection activates Beads, never a `.beads/`
directory, binary or endpoint; nothing probes, initializes or writes an unselected
tracker, and a suspended one gets no command and no substitute. Each bead change is
checked against registered state, integration history, measured reality and integrated
code; the bead, never reality, is corrected, and a retired premise closes as obsolete.
Conclusive inventories are unbounded and flat; other reads stay bounded. A claim needs a
live owner, a deferral a current gate, a closed parent no open child; bugs stay at root.
Each tracker has one curation owner, each close carries one decisive proof, and staleness
never closes a real demand. Bulk writes go in small recorded batches, each bead re-read
first. `TODO.md` is AI Hub's generated view of open issues, never an input.

For Marlon's projects, OpenViking is the primary memory. On session start, resumption
and plan revision, retrieve the global preference and the project checkpoint. Apply
FLEXT SOP and DONE. Reconcile memory, ADRs, the selected tracker and operations docs
with Git, CI and observed runtime. Land this alignment first on the integration tip
with a non-fast-forward merge. Verify setup, fast primary check and fast offline tests
on the integrated SHA. Record the SHA, CI run and next bead in OpenViking. Update
the checkpoint at each milestone and follow execution through final acceptance.
Ask the operator when a material conflict survives verification and continue independent work.
