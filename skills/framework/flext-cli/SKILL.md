---
name: flext-cli
description: 'flext cli routes, declarative commands, result handlers, framework execution'
metadata:
  aihub.tags: '["activation:detected","decision:ADR-0014","detect:dependency:python:flext-cli","detect:selected-tag:flext","effective:2026-09-17","extends:flext-development","route:project","subject:flext","subject:python","usage:on-demand"]'
---

# FLEXT CLI routes

Activate for a detected internal FLEXT consumer when adding or changing CLI
commands: declarative `ResultCommandRoute` registration, typed input models,
`p.Result`-returning handlers, success formatters, exit semantics, or the
framework execution boundary. Do not activate for Result composition
semantics (`$flext-result`), service layering (`$flext-service`), or config
ownership deltas.

Load `$flext-development` and its ancestors first; this child owns only the
route contract. Project code never imports `typer` or `click` and never
builds commands by hand: `flext_cli._utilities.framework` is the single
private adapter behind `p.Cli.Application`. Read
[the route procedure](references/procedure.md) before edits.

Route law: one frozen `m.Cli.ResultCommandRoute` per command — `name`,
`help_text`, `model_cls`, `handler`, then `success_message`,
`success_formatter`, `success_type`. Handlers receive the framework-validated
input model and return `p.Result`; the framework resolves the success message
(formatter, then value-derived, then static), emits it, and owns every exit
path. Register through `register_result_routes` (batch) or
`register_result_route`; execute only through `u.Cli.framework_execute` for
adapter-owned apps, `execute_external_command` for foreign Click commands,
and `u.Cli.run*` for subprocess bridging. Never parse `argv`, print success,
or call `sys.exit` inside route or handler code.
