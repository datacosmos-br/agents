# FLEXT CLI declarative route procedure

Grounded in the `flext-cli` runtime and its real consumer `ai_hub/cli.py`. Verify
installed signatures before editing; the facade is the contract.

## Owners

| Capability                  | Owner                                                                                                                             | Source (under `flext_cli/`)                   |
| --------------------------- | --------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------- |
| Route model                 | `m.Cli.ResultCommandRoute`                                                                                                        | `_models/_base/flextclimodelsbase_part_03.py` |
| Registration                | `FlextCliCli.register_result_routes` / `register_result_route`; imperative `register_result_command` / `register_result_callback` | `services/_cli_parts/flextclicli_part_05.py`  |
| Model-to-command            | `FlextCliCli.model_command`                                                                                                       | `services/_cli_parts/flextclicli_part_03.py`  |
| Private Click/Typer adapter | `u.Cli.framework_*`                                                                                                               | `_utilities/framework.py`                     |
| Output emission             | `u.Cli.commands_resolve_success_message`, `commands_emit_success_message`, `commands_emit_result_error`                           | `_utilities/commands.py`                      |
| Subprocess bridging         | `u.Cli.run_raw`, `run`, `run_checked`, `run_live`, `capture`                                                                      | `_utilities/_runtime_commands.py`             |

## Route contract

`ResultCommandRoute` is a frozen, `extra="forbid"` Pydantic model — the only data-shaped
command declaration:

- `name` (`t.NonEmptyStr`, kebab-case), `help_text`.
- `model_cls` — Pydantic input class; `model_command` maps each non-`exclude` field to
  one keyword-only CLI option (required field → required option, default from the
  field). An empty strict model such as the consumer's `NoArgsInput` yields a
  zero-argument command.
- `handler` — takes the validated model, returns `r[...]`; registration re-wraps it
  through a typed `ResultCommandHandler[M, TResult]` executor.
- `success_message` (static fallback), `success_formatter` (`Callable[[TResult], str]`),
  `success_type` (`c.Cli.MessageTypes`, default `SUCCESS`).

Input models live on the project's `m` facade (real consumer: strict `CityEnterInput`
with one annotated `agent` field). The framework validates argv into the model before
the handler runs; handlers never parse argv.

## Registration

`register_result_routes(app, routes)` loops `register_result_route`, which wraps the
handler in `route_execute` (failure → `r.from_failure`, success → `r.ok`) and delegates
to `register_result_command`. The imperative forms are for one genuine one-off; a second
call with the same keyword shape is a route table waiting to be extracted.

## Executor and exit semantics

`_build_result_executor` owns every outcome:

1. Failure → `u.Cli.framework_exit_result(result)`: inside a framework execution it
   emits the structured error (`commands_emit_result_error` with
   `error_code`/`error_data`/`exception`; traceback only when `settings.cli_verbose`),
   captures the failure, exits 1. Outside, the executor calls
   `cls.exit(code=cls.finalize_result(result))` — `framework_exit` raises `typer.Exit`
   only during an adapter execution, else `SystemExit`; a real exception always escapes
   untouched.
2. Success → `commands_resolve_success_message`: `success_formatter(value)` first, else
   a `message` key or plain string in the JSON-normalized value, else the static
   `success_message`; no message → no output. Emission renders per `success_type`,
   passing JSON-looking text raw.

`framework_execute` normalizes exits into `p.Result[bool]`: usage errors (click's and
typer's vendored `ClickException`) → `e.fail_validation`; `typer.Exit`/`SystemExit`
carrying a captured failure → `r[bool].from_failure`; non-zero int return → typed
failure; success → `r[bool].ok(True)`. The outermost presenter (consumer:
`AiHubCli.present_failure` → `commands_emit_result_error` + `SystemExit(1)`) is the
single process-contract point: success exit 0, typed failure exit 1.

## Choosing the execution boundary

| Need                                      | Owner                                                                                                                                               |
| ----------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| Run the adapter-owned app                 | `FlextCliCli.execute_app` → `u.Cli.framework_execute`                                                                                               |
| Foreign Click-compatible command object   | `execute_external_command` → `u.Cli.framework_execute_external`                                                                                     |
| Expose own app as a foreign Click command | `external_command` → `u.Cli.framework_external_command`                                                                                             |
| External binary / subprocess              | `u.Cli.run` (fails on non-zero), `run_raw` (raw `CommandOutput`), `run_checked` (bool), `run_live` (inherited streams), `capture` (stripped stdout) |
| Drive the real CLI in tests               | `invoke_app` → `u.Cli.framework_invoke` (CliRunner, forced `NO_COLOR`)                                                                              |

`framework_execute` runs your own model-backed app inside the exit-normalizing boundary;
`run_raw` runs an external argv as data. Never subprocess your own app; never import
`typer`/`click` for a command object the facade already exposes.

## Consumer wiring (`AiHubCli`, `ai_hub/cli.py`)

1. Build once: `create_app_with_common_params(name=..., help_text=...)` installs the
   shared global-flags callback.
2. Register once: `register_result_routes(self._app, self.result_routes())`.
3. Route table as data: `(name, help_text)` specs from consumer constants plus
   `(name, help_text, model, handler)` config tool-command rows.
4. Resolve lazily: `_model_cls` derives `"<command> Input"` names (`city-enter` →
   `CityEnterInput`) from `m`; `_handler` binds
   `partial(self._invoke_route, operation)`, resolving the bound service method on first
   run so `--help` stays cheap.
5. `run()` → `execute_app`; `main()` defaults argv, then `present_failure`.

## Before/after 1: hand-rolled typer command → typed route

Before (upstream typer shape — a defect in project code; only
`flext_cli/_utilities/framework.py` may hold it):

```python
import typer

@app.command(name="city-enter")
def city_enter(agent: str = typer.Option(...)) -> None:
    if not agent:
        typer.echo("agent is required")   # hand-rolled validation + output
        raise typer.Exit(code=1)          # hand-rolled exit semantics
```

After (real consumer code): strict input model `CityEnterInput` on `m`; the handler
`city_enter(cls, params) -> p.Result[bool]` (`services/city_entry.py`) validates the
rig, bridges the external `gc` binary through `u.Cli.run_live`, and returns `r.ok(True)`
or `r.from_failure(...)`; and one declarative route — the `city-enter` spec row or a
config row:

```yaml
commands:
  - name: crg-status
    help_text: Validate and report the active graph for an exact Git HEAD.
    model: CrgStatusInput
    handler: crg_status
```

Validation, help, output, and exit codes moved into the framework; the handler is typed
business logic returning `p.Result`.

## Before/after 2: imperative keyword soup → route table

Before (real imperative API; acceptable once, a defect as a pattern):

```python
cli.register_result_command(app, name="agent-list", help_text="...",
    model_cls=NoArgsInput, handler=svc.agent_list, success_message="listed")
cli.register_result_command(app, name="city-enter", help_text="...",
    model_cls=CityEnterInput, handler=svc.city_enter, success_message=None)
```

After (real `AiHubCli`): a data tuple and one call:

```python
def _register_commands(self) -> None:
    AiHubCli.flext_cli().register_result_routes(self._app, self.result_routes())

def result_routes(self) -> tuple[m.Cli.ResultCommandRoute, ...]:
    specs = tuple((name, help_text, None, None)
                  for name, help_text in c.<Facade>.CLI_RESULT_ROUTE_SPECS)
    tools = tuple((cmd.name, cmd.help_text, cmd.model, cmd.handler)
                  for tool in config.<Facade>.tools.tools
                  for cmd in tool.commands)
    return tuple(self._route(spec) for spec in specs + tools)
```

Adding a command becomes one spec/config row plus its `m` input model and service
handler — no registration-code change; the table is inspectable data.

## Verification

Prove the real CLI before tests: register the routes, then drive `invoke_app` or
`execute_app` with an explicit argv — assert exit 0 with the resolved success message
and exit 1 with the structured failure (`error_code`/`error_data` preserved). A route
whose handler or input model cannot be resolved from the real facade fails closed:
request the exact missing contract; never invent a handler, register a placeholder, or
hand-roll a command. Then run the native Make gates.
