---
name: gascity-docs
description: 'project docs, writing conventions, ia structure, verification gates'
metadata:
  aihub.tags: '["activation:opt-in", "detect:opt-in:gascity-docs", "domain:gas-city", "policy:atomic-effects", "policy:causal-subprocess", "policy:fail-loud", "policy:no-fallback", "policy:preflight-before-effects", "policy:strict-execution", "provenance:agents-owned", "route:agent", "technology:gas-city", "updates:manual", "usage:on-demand"]'
---

# Project Documentation

Conventions for writing, editing, restructuring, or reviewing documentation across every project under management. Applies whenever you touch anything in `docs/` (pages, tutorials, guides, reference, ADRs, concept pages, diagrams, navigation), `AGENTS.md`, `README.md`, or prose about project architecture — even when the request is just "fix the docs", "write a docs page", "the docs are wrong/confusing", "rename X across the docs", or an edit to a file under `docs/`. Defines the canonical project model, required terminology, prose / emphasis / diagram conventions, information architecture, the rule that generated docs are edited at their source, and the gates to run before docs work is done. Follow the complete
[router procedure](references/router-procedure.md) and preserve its owners,
evidence contracts, failure propagation, and required output standard.
