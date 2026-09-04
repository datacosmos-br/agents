---
name: pr-sheriff
description: 'pull requests, review triage, github workflow'
allowed-tools: Bash(ai-hub *), Bash(gh *), Bash(git *)
metadata:
  aihub.tags: '["activation:opt-in","decision:plan-00","detect:opt-in:pr-sheriff","effective:2026-08-29","policy:atomic-effects","policy:causal-subprocess","policy:fail-loud","policy:no-fallback","policy:no-keyring","policy:preflight-before-effects","policy:required-environment","policy:strict-execution","policy:zero-residue","provenance:agents-owned","route:agent","tool:github","updates:manual","usage:on-demand"]'
  author: .agents
  version: 3.1.0
---

# PR Sheriff

Activate only for explicit pull-request triage or landing in one repository selected by active configuration. Never infer a repository or scan an organization. Follow the complete `router procedure` (skill file) and preserve its owners, evidence contracts, failure propagation, and required output standard.

Resolve repository ownership and access classification from the repository's
active local configuration before selecting any forge capability. Use AI Hub as
the account and identity authority only when that configuration explicitly
selects its managed-private contract. Public and other-owner repositories never
select AI Hub merely because it is installed. Then use `gh` and `git` directly
for PR evidence. Never run a Python helper directly or through its shebang, and
never create, include, or edit `~/.ssh/config`; repository-specific SSH
selection belongs in local Git configuration.

Use the `PR Sheriff review triage` (skill file) procedure for the mechanical loop, decision rules, and landing traps; preserve the canonical router contract.
