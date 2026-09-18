---
description:
  Associated projects deploy immutable integrated artifacts through staged atomic
  activation.
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-09-04","route:project"]'
---

# Project deployment lifecycle

An associated project moves through `discovered`, `associated`, `development`,
`release_candidate`, `staged`, and `active`. A failed transition retains the previous
valid state and propagates the causal error; it never reports a skip, fallback, partial
success, or alternate deployment.

Build from the integrated commit, publish one immutable versioned artifact with digest,
install outside source checkouts, validate the native public runtime in staging,
activate atomically, and prove version, commit, configuration identity, and behavior
after activation. Development or an editable checkout is never production evidence.
Rollback is attributable cleanup only and does not turn a failed deployment green.

For a `third_party_fork`, use the upstream layout, language level, build system, tests,
and style. Local governance owns only source/upstream identity, delta provenance,
artifact integrity, deployment configuration, and runtime proof.
