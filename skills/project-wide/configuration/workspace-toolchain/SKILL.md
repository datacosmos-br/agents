---
name: workspace-toolchain
description: 'tool layers, binary owners, workspace generators, host boundaries'
license: MIT
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-08-29","usage:router"]'
  version: 1.0.0
---

# Workspace Toolchain

Activate when a task needs a binary, runtime dependency, PATH surface, tool
pin, local environment, or a decision about where that tool belongs. General
code changes without a tool-ownership question do not activate it.

Resolve the tool layer and its one canonical owner before any effect. Host
tools, project fleet tools, project-specific tools, and development
dependencies have different owners and generators; a host decision never
becomes a project pin by proximity or convenience. Follow the
`ownership procedure` (skill file) for the exact routing and
runtime proof.

Never write a generated tool surface by hand or add an undeclared PATH entry,
alias, checkout dependency, keyring, retry, fallback, or duplicate installer.
The first missing owner, conflicting owner, invalid pin, failed generator, or
failed runtime check stops the workflow unchanged.

- Dependency floors vs ceilings: floors written into flext-infra
  `config/codegen.yaml` `dependency_profiles` must never exceed a transitive
  ceiling coming from another member's third-party dependency (resolver cannot
  satisfy floor > ceiling, e.g. click floored 8.5.0 against meltano's
  `click<8.4`). When adding/raising a floor a third-party package caps, keep
  the floor <= ceiling and record the ceiling in the profile comment.
- System-owned binaries vs mise: `make`, `curl`, and `git` are
  system package-manager binaries — never declare them as mise-managed tools.
  Mise shims for them break bootstrap credential paths and PATH resolution;
  the host package manager is their only owner.
