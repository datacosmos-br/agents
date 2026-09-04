---
globs: **/*.py
---

# Read configuration only through the typed config/settings SSOT

Access every value via `from ai_hub import config, settings`, then
`config.AiHub.<domain>` / `settings.AiHub.<domain>` — each returns a validated
typed model, never a raw dict.

- config = fixed business rules; settings = anything the user can parametrize.
- No `os.environ[...]` reads, no `ECC_HOME`/`*_ENV`, no custom `*_home()` helper,
  no duplicated SSOT. Fixed value -> config; user override -> settings.
- Tests vary valid config/settings values and validate schema, types, invariants,
  derivations, precedence, round-trip, consumer behavior, and generated structure.
  Never assert today's config-owned IDs, paths, endpoints, models, rankings,
  defaults, or scalars. Derive expectations from test input or typed SSOT.
