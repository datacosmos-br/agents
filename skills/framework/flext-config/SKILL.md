---
name: flext-config
description: 'flext settings, flext config, frozen config singleton, env expansion, config repoint'
metadata:
  aihub.tags: '["activation:detected","decision:ADR-0014","detect:dependency:python:flext-core","detect:selected-tag:flext","effective:2026-09-17","extends:flext-development","route:project","subject:flext","subject:python","usage:on-demand"]'
---

# FLEXT settings vs config ownership

Activate when a FLEXT project task decides where a value lives - `FlextSettings`
external inputs (environment variables, `.env`, nested sources) versus
`FlextConfig` governed YAML `config/*.yaml` - or touches expansion placeholders,
the `fetch_global` singletons, repointing settings/config in tests, or how a
service may consume them. Do not activate for generic Pydantic modeling, schema
cutover, result-railway composition, or service composition that raises no
settings/config ownership question.

Compose `$flext-development` first; it already composes `$py-dev` and `$solid`.
This skill owns only the settings/config ownership delta.

Read the `ownership procedure` (skill file). Settings loads external inputs and
stays mutable through its owner (`fetch_global`/`update_global`/`clone`); config
derives one validated frozen root from governed YAML and is read-only. Services
consume explicit parameters or the validated global facades - never
`os.environ`, `Path.home`, or a re-parsed file. Placeholder residue, a patched
config ClassVar, or a second answer to one directory question fails before
effects.
