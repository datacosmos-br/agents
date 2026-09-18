---
name: openspec-verify
description: "openspec, change verification, specification evidence"
license: MIT
compatibility: Requires openspec CLI.
metadata:
  aihub.tags: '["activation:detected","decision:ADR-0008","detect:marker:openspec","effective:2026-08-28","route:project","subject:openspec","supersedes:skill:openspec-verify-change","usage:on-demand"]'
  author: openspec
  version: "1.0"
  generatedBy: 1.1.1
---

# OpenSpec Change Verification

Activate only when the project marker and installed owner interface are present. Require
one explicit change identity; ambiguity stops without choosing a target.

Read the selected status, owner-returned context, requirements and scenarios, accepted
design, implementation, and project-native tests. In declared order, map each
requirement and scenario to exact observable implementation and test evidence, and
verify coherence with the accepted design. Keyword matches and task checkmarks are not
evidence.

The first missing, unreadable, conflicting, or behaviorally divergent item is a blocking
verification failure. Preserve its raw CLI or filesystem cause and stop independent
classification; never turn it into a warning, suggestion, skip, finding, retry,
fallback, or partial verified claim.

Verification is read-only. Do not mutate status, tasks, change artifacts, code, tests,
or tracker state. Report the exact proven prefix and first blocker, or a fully evidenced
result when no blocker exists.
