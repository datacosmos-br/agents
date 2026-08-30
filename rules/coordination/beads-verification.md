# Bead verification is critical and mandatory

Every bead — at creation, at every update, and before close — declares and
passes a critical cross-check against four independent sources:

1. **Registered state records** — the authorized state documents, handoffs
   and receipts. A bead contradicting its ledger is corrected at the ledger's
   owner, never silently.
2. **Git history** — real commits and merged PRs on the integration lane.
   Work is not done because a bead says so; it is done when the lane carries
   it.
3. **Measured reality** — disk, processes, receipts, live endpoints, with
   command, working directory, exit code and decisive output.
4. **The intent of the most recent code** — the integrated HEAD, not an
   older revision. A bead whose premise the current code or the current law
   retired is closed as obsolete with the evidence, never executed as
   written.

The bead is the hypothesis; reality is the proof. Closing without the
four-source declaration plus evidence is a violation, never a shortcut.
Divergence between bead and reality is fixed in the bead — never in reality.

Orchestration surfaces that must carry this rule: the city `AGENTS.md`,
the tracker prime override (what the tracker prints at session start), and
every city skill. A surface that does not carry it is a defect.
