---
name: context7-documentation
description: 'context7, library documentation, versioned references'
metadata:
  aihub.tags: '["activation:opt-in","decision:plan-00","detect:opt-in:context7","detect:selected-tag:documentation","effective:2026-08-29","policy:causal-subprocess","policy:fail-loud","policy:no-fallback","policy:no-keyring","policy:preflight-before-effects","policy:required-environment","policy:strict-execution","policy:zero-residue","provenance:agents-owned","route:project","tool:context7","updates:manual","usage:on-demand"]'
---

# Context7 Documentation

Activate only for an explicit current external library, framework, or API
documentation lookup. Repository-owned documentation does not activate it.

Before a tool call, resolve the exact library/package and import evidence,
requested version, question, current Context7 capability, and any non-derivable
current-process credential. Reject ambiguous identity, absent version evidence,
secret-bearing query text, or an unavailable owner before sending data.

Use the current callable owner interface to resolve one official,
version-compatible documentation identity, then fetch the specific documentation
needed to answer. Do not copy tool names or signatures from this skill, switch
libraries or versions, query an alternate provider, use cached profiles, or fill
gaps from remembered APIs.

The first transport, resolution, or documentation failure propagates unchanged;
do not retry or answer from partial snippets. Return a material answer grounded
only in fetched documentation and identify the selected library, version, and
source. A lookup that cannot produce that evidence produces no answer artifact.
