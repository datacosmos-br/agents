---
name: x-api
description: 'x api, social publishing, external integration'
metadata:
  aihub.tags: '["activation:opt-in","decision:ADR-0008","detect:opt-in:x-api","effective:2026-08-28","policy:atomic-effects","policy:causal-subprocess","policy:fail-loud","policy:no-fallback","policy:no-keyring","policy:preflight-before-effects","policy:required-environment","policy:strict-execution","policy:zero-residue","provenance:agents-owned","route:agent","tool:x-api","updates:manual","usage:on-demand"]'
---

# X API

Activate only for an explicit X API read or publication. Discussion of the
letter X, supplied social text, or work owned by another publisher does not
activate it.

Before any network call, resolve the current official interface and schema,
exact account, operation, payload, authorization context and scopes, operator
approval, rate/cost boundary, effect count, expected response, and required
current-process credentials. Reject missing or conflicting evidence before
sending data. Never use keyring, profiles, credential files or aliases.

For publication, preserve the approved payload byte-for-byte and execute exactly
the approved atomic effect. A multi-request thread or media flow is allowed only
when the current owner provides an atomic or fully compensating contract proven
before the first request; otherwise refuse it. Do not add posts, media, replies,
or analytics implicitly.

Use one endpoint and auth context derived from current owner evidence. The first
HTTP, transport, rate-limit, authorization, schema, timeout, or signal failure
propagates unchanged. Do not retry a rate limit, back off and resubmit, switch
endpoint/auth/provider, or normalize failure into success. Report only observed
response identity and reset evidence, and remove staged residue on failure.
