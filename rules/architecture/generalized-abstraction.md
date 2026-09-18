---
description: Generalize from real consumers
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-08-25","route:both"]'
---

# Generalize from real consumers

Search existing owners first. Extend one generalized reusable owner or type and rewire
every current consumer; do not create a named one-off component. Remove the same
pre-existing in-scope offender in the cutover. YAGNI forbids abstractions without a real
current consumer.

Repository artifact visibility has one owner: its `.gitignore`. Extend the existing
Git-aware file-inventory facade and rewire scanners to it; never copy cache or
build-artifact name lists into commands, services, gates, agents, or tool-specific
configuration.

A config placeholder such as `${AI_HUB}` has exactly one expander: the typed loader that
owns its schema. No other code re-expands, re-substitutes, or hardcodes that
placeholder's resolved value. A second expander — for example a write-guard that
substitutes the literal with its own constant — is a SSOT violation even when both
owners agree today: the two paths diverge silently on the next change, surfacing as a
`KeyError` in CI or an ambiguous test that fails for the wrong reason. Fix the duplicate
at its owner: delete the second expansion path and route every consumer through the one
loader.
