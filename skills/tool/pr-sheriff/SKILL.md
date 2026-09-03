---
name: pr-sheriff
description: 'pull requests, review triage, github workflow'
allowed-tools: Bash(gh *), Bash(git *)
metadata:
  aihub.tags: '["activation:opt-in","decision:plan-00","detect:opt-in:pr-sheriff","effective:2026-08-29","policy:atomic-effects","policy:causal-subprocess","policy:fail-loud","policy:no-fallback","policy:no-keyring","policy:preflight-before-effects","policy:required-environment","policy:strict-execution","policy:zero-residue","provenance:agents-owned","route:agent","tool:github","updates:manual","usage:on-demand"]'
  author: .agents
  version: 3.1.0
---

# PR Sheriff

Activate only for explicit pull-request triage or landing in one repository selected by active configuration. Never infer a repository or scan an organization. Follow the complete `router procedure` (skill file) and preserve its owners, evidence contracts, failure propagation, and required output standard.

The bundled script is Python-stdlib-only and declares its complete external
executable allowlist as `gh` and `git`. Selecting this skill selects those
executables only for the configured repository; installation alone does not.

Use the `PR Sheriff review triage` (skill file) procedure for the mechanical loop, decision rules, and landing traps; preserve the canonical router contract.
