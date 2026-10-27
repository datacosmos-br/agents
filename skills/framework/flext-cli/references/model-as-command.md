# FLEXT-INFRA model-as-command routes

Read this alongside [the route procedure](procedure.md), which owns the
`ResultCommandRoute` fields, model-to-option mapping and framework exit semantics.
Verify the current `flext-infra` sources before changing a route. Paths below are
relative to `flext_infra/`.

## Owners

| Capability | Owner | Source |
| ---------- | ----- | ------ |
| Group selection | `FlextInfraCliRouteService.route_table_for` | `services/cli_routes.py` |
| Check, codegen and deps routes | `FlextInfraCodegenRoutes.check_routes`, `codegen_routes`, `deps_routes` | `services/cli_routes_codegen.py` |
| Release and workspace routes | `FlextInfraWorkspaceRoutes.release_routes`, `workspace_routes` | `services/cli_routes_workspace.py` |
| Refactor routes | `FlextInfraRefactorRoutes.refactor_routes` | `services/cli_routes_refactor.py` |
| Docs, maintenance and validate routes | `FlextInfraValidationRoutes.validation_routes` | `services/cli_routes_validate.py` |
| Group execution | `FlextInfraCliDispatchService.run_group` | `services/cli_dispatch.py` |
| Service-model delegation | `FlextInfraServiceBase.execute_command` | `base.py` |

## Model and handler binding

The input class remains concrete at registration: `model_command` reads its
`model_fields` to construct help and options. Annotated fields and their aliases
define the CLI surface. Collaborators declared with `exclude=True` remain internal.

When the input model is the service, its unbound `execute` method receives the
validated service instance. Dependency routes use `handler=model_cls.execute`;
the operation's domain result remains typed inside that service. The existing
`execute_command` seam delegates to the validated instance where a route uses it.

When the input and operation have different owners, bind the existing public
facade, `execute_payload` or `execute_request` boundary appropriate to that
operation. Generation and conformance use the existing `execute_codegen_generate`
and `execute_codegen_conform` handlers to erase their receipts to the CLI result
type while propagating failures. Reuse those owners instead of adding another
handler-erasure layer.

Keep `workspace_propagate` bound to `flext_infra.infra.workspace_propagate`:
that facade injects the propagation collaborators.

## Group construction and execution

`route_table_for(group)` selects one owner through the existing public `services`
barrel. The check/codegen/deps and release/workspace factories return ordered tuples
of native `m.Cli.ResultCommandRoute` models. Each factory resolves only its own
group's models and handlers. Refactor and validation retain their existing owners.

The owners of these five factories use the existing public lazy barrels
(`codegen`, `deps`, `workspace`, `check`). Their access to `flext_infra.infra`
occurs inside a selected factory or the operation's handler. The validation owner
still constructs its shared mapping eagerly, and the refactor owner still
constructs its tuple eagerly when imported. Shared facades and dependencies of
the selected group still load; this structure alone proves no measured startup
improvement or per-command lazy loading.

The dispatcher registers the selected tuple through `register_result_routes` and
executes the app through the framework. Registration, output and exit semantics
remain with `flext-cli`.

## Adding a command

1. Define the concrete input model or service model on its declared owner. Annotate
   CLI fields, preserve their aliases and exclude internal collaborators.
2. Add the native route to the selected group's existing factory or table. Preserve
   its order, handler, success message, formatter and message type.
3. Use `route_table_for` when consuming a group; keep the group selector in that
   owner. Do not introduce a parallel registry, cross-group eager table or cache.
4. Exercise the real public route and its failure behavior before changing tests.
   Then validate through the repository's declared root Make verbs.
