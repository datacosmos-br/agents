---
description: Editing configuration, generated surfaces, or hardcoding a value. Load when changing config, settings, templates, tool homes, systemd units, or goldens.
---

# Edit canonical sources, regenerate projections, prove idempotence

config, settings, and templates are the only source of configuration and
business rules; the correct generator produces every derived surface. Never
hand-edit a generated projection (tool homes, `{config.AiHub.agents.agents.cursor.home}/rules`,
systemd units, goldens).

- No product-, agent-, or daemon-specific hardcoded value anywhere — parametrize
  it. Each managed binary is installed by its declared local owner.
- After changing a source, regenerate and prove a second generation has no diff.
