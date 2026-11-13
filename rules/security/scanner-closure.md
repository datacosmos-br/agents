---
description: Reproducible scanner findings block closure until fixed and rerun clean
metadata:
  aihub.tags: '["decision:ADR-0038","effective:2026-11-03","route:both"]'
---

# Security findings block closure

Every reproducible finding of a released scanner, at any severity, blocks closure until
its owner source is corrected and a clean rerun of that scanner proves it, with the
decision and evidence on the tracker item. Project `docs/security/*-triage.md` files are
evidence reports, never task trackers. A false-positive or compatibility classification
needs reproducible proof, measured for compatibility against the project's declared
language and runtime support, and the operator's explicit authorization after
discussion. Risk acceptance, ignore files, inline suppressions such as `nosemgrep`,
masked exit codes, vulnerable old and new code side by side, an unverified base-image
change, and capping, downgrading or replacing the scanner never close a finding.
