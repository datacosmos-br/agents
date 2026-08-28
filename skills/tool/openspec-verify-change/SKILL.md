---
name: openspec-verify-change
description: 'Verify OpenSpec changes when a local openspec directory proves the workflow.'
license: MIT
compatibility: Requires openspec CLI.
metadata:
  aihub.tags: '["activation:detected","detect:marker:openspec","provenance:agents-owned","route:project","tool:openspec","updates:manual","usage:on-demand"]'
  author: openspec
  version: '1.0'
  generatedBy: 1.1.1
---

# OpenSpec Change Verification

Use only when the project contains the OpenSpec marker and the installed CLI
confirms the requested interface.

1. If no change is named and more than one candidate exists, stop for an explicit
   selection; never infer a target from proximity or status.
2. Read the selected change status and the CLI-returned context files.
3. Verify completeness: every task and requirement has implementation evidence.
4. Verify correctness: each requirement and scenario maps to observable behavior
   and a project-native test where appropriate.
5. Verify coherence: implementation follows accepted design decisions and the
   repository's established patterns.
6. Classify missing implementation as blocking, material divergence as a warning,
   and optional improvement as a suggestion. Cite exact evidence paths.

Do not mark tasks complete, mutate artifacts, or claim conformance from keyword
matches. CLI errors, ambiguous targets, unreadable context, and missing evidence
remain explicit failures.
