# FLEXT-INFRA model-as-command routes

Grounded in the real `flext-infra` sources (paths under `flext_infra/`). This is
the framework-side sibling of [the route procedure](procedure.md): procedure.md
owns the consumer contract (`ResultCommandRoute` fields, `model_command`
field-to-option mapping, success/exit semantics); this page owns the
flext-infra authoring form — the command model IS the service class, and the
handler is derived from it.

## Owners

| Capability             | Owner                                       | Source (under `flext_infra/`)   |
| ---------------------- | ------------------------------------------- | ------------------------------- |
| Handler erasure        | `CliRouteBase.result_handler`               | `services/cli_route_base.py`    |
| Check/codegen/deps table | `CodegenRoutes.codegen_routes`            | `services/cli_routes_codegen.py`|
| Per-group lazy resolve | `CliRouteService.route_table_for`           | `services/cli_routes.py`        |
| Group dispatch         | `CliDispatchService.run_group`              | `services/cli_dispatch.py`      |
| Service-as-model seam  | `FlextInfraServiceBase.execute_command`     | `base.py`                       |

## The mechanism

1. The service class is a Pydantic model. `FlextInfraServiceBase` declares the
   abstract `execute() -> p.Result[TDomainResult]` plus one classmethod seam,
   `execute_command(cls, params: Self) -> p.Result[TDomainResult]` — the
   framework-validated model instance is the service (`base.py:146-159`).
2. The CLI surface comes from the fields. Annotated model fields become
   options (`output_format` with `alias="format"`, `no_fail` with
   `alias="no-fail"`); service collaborators are `m.Field(exclude=True, ...)`
   with `default_factory` (consumer: `deps`, `runner` in
   `deps/detector.py:47-54`) so they never become flags.
3. The handler is derived, never written. `model_cls.execute_command` already
   has the `Callable[[TParams], p.Result[TResult]]` shape;
   `CliRouteBase.result_handler` wraps it and erases the concrete payload to
   `t.Cli.ResultValue` via `.map(as_route_value)` — the table is heterogeneous,
   so each command's `TResult` is erased at that one boundary
   (`services/cli_route_base.py:19-25`).
4. The route table is `ClassVar` data keyed by group constant
   (`services/cli_routes_codegen.py:36-38`). Deps rows carry only
   `(route_name, help_text, model_cls)` and the generator derives the handler
   (`services/cli_routes_codegen.py:207-231`):
   `handler=CliRouteBase.result_handler(model_cls.execute_command)`. The split
   shape — separate input model plus service payload handler (`m.Infra.RunCommand`
   - `FlextInfraWorkspaceChecker.execute_payload`) — stays available when the
   operation lives on another class than the input model.
5. Resolution is per group, lazily. `CliRouteService.route_table_for(group)`
   imports only the dispatched group's owner module inside a `functools.cache`
   classmethod backed by `_GROUP_OWNERS` (`services/cli_routes.py:23-104`).
   Building every group's table at class-definition time eagerly imported all
   owner modules on every invocation (~5.9s measured via
   `python -X importtime`) — the regression this layout guards against.
6. Registration is the same facade call as any consumer:
   `CliDispatchService.run_group` builds the group app with
   `create_app_with_common_params`, registers via
   `register_result_routes(app, self.route_table_for(group))`, runs
   `execute_app`, then maps the returned `p.Result[bool]` to process exit codes
   (`services/cli_dispatch.py:72-106`). The same shape repeats in
   `ValidationRoutes` and `WorkspaceRoutes`.

## Adding a flext-infra command

1. Author the service model: subclass the selection/service base, annotate the
   CLI fields (aliases for multi-word flags), mark collaborators
   `exclude=True`, implement `execute() -> p.Result[...]`.
2. Append one data tuple `(route_name, help_text, model_cls)` to the owning
   group's table in `services/cli_routes_codegen.py` (or its validate/workspace
   sibling).
3. Nothing else changes: the group constant, lazy table, and dispatch pick the
   row up; drive it as `flext-infra <group> <route_name>`.

## Laws

- Never write a handler lambda or a bespoke `register_result_command` call
  where `result_handler(model_cls.execute_command)` derives it.
- Never import a route-owner module at module scope outside the lazy
  `_GROUP_OWNERS` path — eager imports re-create the startup regression.
- Never expose a collaborator service or runner as a CLI field without
  `exclude=True`.
- Never widen the erasure: concrete `TResult` flows inside `execute()`; only
  the heterogeneous table boundary sees `t.Cli.ResultValue`.
