---
description: Editing configuration, generated surfaces, or hardcoding a value. Load when changing config/settings/templates, tool homes, mcp/generated, systemd units, goldens, or config.AiHub.agents.agents.cursor.home rules.
---

# Edit canonical sources, regenerate projections, prove idempotence

config, settings, and templates are the only source of configuration and
business rules; the correct generator produces every derived surface. Never
hand-edit a generated projection (tool homes, `{config.AiHub.agents.agents.cursor.home}/rules`,
`mcp/generated`, systemd units, goldens).

- No product-, agent-, or daemon-specific hardcoded value anywhere — parametrize
  it. ai-hub owns binary installation.
- After changing a source, regenerate and prove a second generation has no diff.
