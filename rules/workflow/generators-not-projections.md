---
description: Editing configuration, generated surfaces, or hardcoding a value. Load when changing config, settings, templates, tool homes, systemd units, or goldens.
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-08-28","route:both"]'
---

# Edit canonical sources, regenerate projections, prove idempotence

config, settings, and templates are the only source of configuration and
business rules; the correct generator produces every derived surface. Never
hand-edit a generated projection such as provider configuration, service units,
or goldens.

- No product-, agent-, or daemon-specific hardcoded value anywhere — parametrize
  it. Each managed binary is installed by its declared local owner.
- Every generated file carries a standardized marker naming its writable owner,
  that hand edits are forbidden, and the exact declared Make regeneration
  command. A generated marker without a resolvable owner is a defect.
- After changing a source, regenerate and prove a second generation has no diff.
- Rewire every consumer before deleting the superseded output. Remove obsolete
  projections, manifests, tests, fixtures, docs, backups, and archives in the
  same cutover; never keep an old and new generator path.
