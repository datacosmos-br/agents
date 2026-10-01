---
description:
  Editing configuration, generated surfaces, or hardcoding a value. Load when changing
  config, settings, templates, tool homes, service units, or goldens.
metadata:
  aihub.tags: '["decision:ADR-0031","effective:2026-10-01","route:both"]'
---

# Edit canonical sources, regenerate projections, prove idempotence

config, settings, and templates are the only source of configuration and business rules;
the correct generator produces every derived surface. Never hand-edit a generated
projection such as provider configuration, service units, or goldens.

- No product-, agent-, or daemon-specific hardcoded value anywhere — parametrize it.
  Each managed binary is installed by its declared local owner.
- Every generated file carries a standardized marker naming its writable owner, that
  hand edits are forbidden, and the exact declared Make regeneration command. A
  generated marker without a resolvable owner is a defect.
- A file such as `AGENTS.md` has no single owner: each piece has its correct owner
  (tracker memory `operator-rulings-2026-10-01-governance`, ruling 5). A block written
  between begin/end markers by ~/agents and AI Hub, the selected tracker, or another
  tool is a projection owned by that writer. The text outside every marker belongs to
  the project. A whole generated file belongs to the owner its marker names. No writer
  creates, rewrites, or removes a piece it does not own: never altering a projected
  part and never crossing a domain are inviolable (same tracker memory, ruling 5).
- Markdown and docs gates exclude a projected block at their SSOT exclude list, never
  by hand-fixing lint inside it. A projected block carries no authority: where it
  contradicts a rule — an `rtk init` block prefixing git with `rtk`, a Beads profile
  running `git pull --rebase` — the rule wins (git stays plain and is never rebased),
  and the block is corrected or removed through its own writer, never hand-edited
  between its markers.
- After changing a source, regenerate and prove a second generation has no diff.
- Rewire every consumer before deleting the superseded output. Remove obsolete
  projections, manifests, tests, fixtures, docs, backups, and archives in the same
  cutover; never keep an old and new generator path.
