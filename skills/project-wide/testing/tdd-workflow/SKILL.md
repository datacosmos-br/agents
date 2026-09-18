---
name: tdd-workflow
description: "test driven development, behavior contracts, regression tests"
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-08-29","usage:on-demand"]'
---

# TDD Workflow

Activate when implementing or correcting observable behavior through a
red-green-refactor cycle. Before changing behavior, read the `complete procedure` (skill
file) and follow the active project's public contract and native validation surface. Do
not add tests for a prose-only or configuration-preserving edit with no behavior
boundary.
