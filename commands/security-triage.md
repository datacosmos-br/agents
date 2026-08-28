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
repository's `docs/security/*-triage.md` as the evidence report. Run
`agentsctl security-triage $ARGUMENTS` before changing code, then use each
project's canonical scanner commands to reproduce every finding.

For each finding, fix the owner source, regenerate derived files, update every
consumer, record the decision and reproducible evidence in the same report, and
rerun the exact scanner. Follow an active project tracker only when its runtime
is authorized; otherwise update the repository-declared manual ledger. Every
severity blocks closure.
A false-positive or compatibility classification requires prior operator
discussion, a precise reproducible technical proof, and explicit authorization.
Use the newest released scanner; never cap, downgrade, substitute, or suppress
it to avoid findings. Risk acceptance, generic ignores, fallbacks, `|| true`,
and unevidenced suppressions do not close findings. Report every command, exit
code, decisive output, affected root, and unresolved blocker.
