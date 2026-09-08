---
name: scope-nav
description: 'code navigation, reference tracing, scope cli'
metadata:
  aihub.tags: '["activation:opt-in","decision:ADR-0008","detect:opt-in:scope-nav","effective:2026-08-28","route:project","subject:scope","supersedes:skill:scope-code-navigation","usage:on-demand"]'
---

# Scope Code Navigation

Activate only for an explicit structural query against a repository with a
current Scope index. A known literal at a known location does not activate it.

Before a Scope call, resolve the checkout and project identity, installed Scope
interface, index ownership and freshness, exact symbol or structural question,
and required blast-radius evidence. If an authorized index refresh is necessary,
validate its target and storage boundary before the first write.

Select the single current structural operation whose discovered schema answers
the question. Do not copy a command catalog from this skill, run redundant query
forms, broaden to repository-wide text search, or treat an index summary as
source evidence. Read only the returned definition and exact relationship sites
needed for the change, then stop navigation before editing.

The first missing checkout, stale index, unknown symbol, command, parse, timeout,
signal, or index-publication failure propagates unchanged. Do not retry, fall
back to another navigator, report a partial call graph, or leave a partial index.
