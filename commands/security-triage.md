---
name: security-triage
description: Validate and close scanner findings from project-owned security triage reports.
argument-hint: "<one or more explicit repository roots>"
metadata:
  aihub.tags: '["intent:verification","risk:write","route:agent"]'
---

# Security triage

Require `$ARGUMENTS` to name one or more explicit repository roots. Reject an
empty, nonexistent, symlinked, or ambiguous root before scanning. Use each
repository's `docs/security/*-triage.md` as the evidence report. Run the
optionless `agentsctl secure` from each physical root before changing code; it
owns that project's complete configured scanner workflow.

For each finding, fix the owner source, regenerate derived files, update every
consumer, record the decision and reproducible evidence in the same report, and
rerun the exact scanner. Follow an active project tracker only when its runtime
is selected, authorized, and available. During suspension, create no substitute
tracker or ledger and preserve evidence only in separately authorized Git/PR/CI.
Every severity blocks closure.
A false-positive or compatibility classification requires prior operator
discussion, a precise reproducible technical proof, and explicit authorization.
Use the newest released scanner; never cap, downgrade, substitute, or suppress
it to avoid findings. Risk acceptance, generic ignores, fallbacks, `|| true`,
and unevidenced suppressions do not close findings. Report every command, exit
code, decisive output, affected root, and unresolved blocker.
