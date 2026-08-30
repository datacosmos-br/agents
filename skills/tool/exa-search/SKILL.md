---
name: exa-search
description: 'exa search, web research, source discovery'
metadata:
  aihub.tags: '["activation:opt-in","decision:plan-00","detect:opt-in:exa","effective:2026-08-28","policy:causal-subprocess","policy:fail-loud","policy:no-fallback","policy:no-keyring","policy:preflight-before-effects","policy:required-environment","policy:strict-execution","policy:zero-residue","provenance:agents-owned","route:agent","tool:exa","updates:manual","usage:on-demand"]'
---

# Exa Search

Activate only for an explicit Exa-backed web, code, company, or people search.
Local repository search and supplied closed sources do not activate it.

Before sending a query, resolve the exact question, result count, date and domain
constraints, source requirements, current Exa MCP capability, cost authority,
and required current-process credential. Reject secrets in query text and any
missing, conflicting, or invalid requirement before the first call.

Select the single current owner operation whose discovered schema satisfies all
constraints; do not copy operation names or defaults from this skill. Execute
the bounded search once, distinguish result snippets from fetched evidence, and
deep-read the decisive primary source once before answering.

The first transport, search, fetch, timeout, or schema failure propagates
unchanged. Do not retry, broaden constraints, switch operation or provider, use
remembered facts, or return a partial answer. Report the material result with
source attribution and the applied constraints; otherwise publish no research
artifact.
