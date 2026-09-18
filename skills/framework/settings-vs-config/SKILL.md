---
name: settings-vs-config
description: "settings vs config, runtime adjustment, static rules, ownership frontier"
metadata:
  aihub.tags: '["activation:detected","decision:ADR-0014","detect:dependency:python:flext-core","detect:selected-tag:flext","effective:2026-09-18","extends:flext-development","route:project","subject:flext","usage:on-demand"]'
---

# Settings vs Config

Activate when a task decides where a value lives. `settings` are runtime-adjustable:
values a user, operator, or running code may change per deployment or per process,
loaded from external inputs (environment variables, `.env`, nested sources), validated
at load, and mutable only through their owner. `config` is static rules: values
declared in governed data (`config/*.yaml`), validated once into a frozen read-only
root, changeable only by a reviewed edit to the data itself. Do not activate for
generic Pydantic modeling, result-railway composition, or service wiring that raises
no ownership question.

Load `$flext-development` and its ancestors first: `$solid`, `$py-dev`, then
`$flext-development`. This child owns only the settings/config ownership frontier,
not schema design, exception policy, or service composition. Apply `$yagni` to
proposed abstraction layers.

Decide with one question: who may change the value, and through which review?

- Varies per environment, per deployment, or by operator action without a reviewed
  data change: a setting. Load it from external inputs, validate at load, expose it
  through its owning facade, and keep that owner the single mutation path.
- Changes only by editing the governed data and shipping that reviewed change:
  config. Declare it in the data file, validate once, freeze the root, consume it
  read-only.
A field gets exactly one home. The same value declared in both places is a defect,
and a field that seems to need both natures is two fields.

Declare each nature in its own model. Never mix runtime-adjustable inputs and frozen
rules in one base model. In FLEXT this split materializes as `FlextSettings` (external
inputs, mutable through `fetch_global`/`update_global`/`clone`) versus `FlextConfig`
(one validated frozen root per governed source); apply the same frontier in any stack.

Violations fail before effects:

- Runtime config mutation: writing a config object, patching a frozen ClassVar, or
  monkeypatching rules after load. If a test needs different rules, repoint or clone
  through the sanctioned owner mechanism; if the product needs the change at runtime,
  the value is a setting, not config.
- Frozen settings: an environment-sourced knob hardcoded or locked so deployments
  cannot vary it. Freezing belongs to config only.
- Catch-based defaults: `try: parse() except: return default` turns a missing or
  invalid external input into a silent fallback. Load failures surface as validation
  errors, never as defaults.
- Point-of-use reads: `os.environ`, `Path.home`, or re-parsing a file inside a service
  method bypasses the validated facade. Services consume injected values or the
  validated global facades.
- Placeholder residue: unexpanded placeholders in loaded data fail the load.

Missing evidence blocks the edit, not an invitation to invent it. Without the source
list, the owner and mutation policy, or the allowed keys/schema, name the missing
contract precisely and stop. Do not guess a key, a default, or a file location.

Remember: settings answer who runs it; config answers what the reviewed data says.
Mutable through the owner versus frozen after validation. One value, one home.
Defaults never catch load failures.
