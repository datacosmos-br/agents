---
name: tdd-workflow
description: "runtime-first behavior, observable contracts, regression validation"
metadata:
  aihub.tags: '["decision:ADR-0031","effective:2026-10-23","usage:on-demand"]'
---

# Behavioral Regression Workflow

Activate when implementing or correcting observable behavior that needs real-runtime proof and subsequent
regression validation. Read the `complete procedure` (skill file) and compose the
documentation-first and runtime-first rule owners before effects. Implement and prove
the actual behavior before changing tests; this procedure has no test-first branch.
Do not add tests for a prose-only or configuration-preserving edit with no behavior
boundary.
