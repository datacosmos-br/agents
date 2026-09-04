---
description: Editing configuration, generated surfaces, or hardcoding a value. Load when changing config/settings/templates, tool homes, MCP routing, systemd units, goldens, or config.AiHub.agents.agents.cursor.home rules.
---

# Edit canonical sources and materialize only at the consuming boundary

Config, settings, and templates are the only source of configuration and
business rules. A runtime consumer renders from those owners in memory and
promotes the accepted bytes directly to its declared use location. A private,
same-filesystem transaction stage may exist only for the duration of validation
and atomic promotion; it is never a readable source, persistent cache, packaged
artifact, or repository projection.

MCP schema, route maps, tool catalogs, package manifests, and agent MCP configs
must never be written below the repository as generated intermediates. In
particular, both `mcp/generated` and `config/generated/mcp` are prohibited and
their presence, declaration, or consumption fails the native gates. Schema and
route maps are derived in memory, catalogs live only in the gateway process,
and agent/systemd surfaces are rendered directly to their real managed targets.
An explicitly declared dependency lock is a reviewed source input; it must not
live under a generated directory and is copied directly into an immutable
release candidate together with its in-memory manifest.

Never hand-edit a runtime-owned target (tool homes,
`{config.AiHub.agents.agents.cursor.home}/rules`, systemd units, goldens). Change
its canonical owner and invoke the direct materializer.

- No product-, agent-, or daemon-specific hardcoded value anywhere — parametrize
  it. ai-hub owns binary installation.
- After changing a source, materialize twice and prove the second invocation
  changes no target bytes and leaves no intermediate residue.
