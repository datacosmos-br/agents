# Static/runtime typing diagnosis

Record the executed Python, Pydantic and checker versions, loaded configuration,
resolved import origins and editor diagnostic source before changing a declaration.
The project's topology and configuration owners select its environment; do not
copy workspace-specific interpreter paths or policies into universal guidance.

Compare upstream declarations with the real public facade across direct and
indirect inheritance, nested models, generic specialization, defaults, aliases,
validators, computed fields and settings. For each case retain the runtime
result, inferred type and diagnostic, including invalid inputs that must still
fail. Distinguish import-resolution failures, declaration defects, export
identity loss and demonstrated checker limitations. A runtime descriptor
preserving a callable is not evidence that the checker recognizes its identity.

The typing specification extends `dataclass_transform` to indirect subclasses;
MRO depth alone does not establish a defect. Pydantic documents limitations for
constructor defaults/factories/aliases stored inside `Annotated` and for
multiple-base configuration composition. Verify these against the installed
version before repair. Preserve the public runtime contract and typed
constructors; further diagnostic changes follow the project's approval policy.
Where the project requires import-time schema completeness, lazy module loading
does not authorize `defer_build=True` after import. Reconcile the preset owner
and prove a fresh public import; a later schema build is different evidence.

External references: [dataclass transforms](https://typing.python.org/en/latest/spec/dataclasses.html),
[Pydantic fields](https://docs.pydantic.dev/latest/concepts/fields/),
[configuration](https://docs.pydantic.dev/latest/concepts/config/) and
[mypy integration](https://docs.pydantic.dev/latest/integrations/mypy/).

## Complete declarations at import

`Model.model_rebuild()` (and `_types_namespace` hacks) exist to patch annotations that
failed to resolve. In a strict fleet, every namespace that declarations depend on —
`config`, `settings`, `c`, `t`, `p`, `m`, `u`, `base.py`, `services/`, `api.py`,
`cli.py` — must resolve through the declaring owner's native namespaces. A required
rebuild is a diagnostic: inspect unresolved exports, import cycles and symbols imported
only for type checking before changing the declaration. A function-local model is not
automatically defective: native Pydantic resolves supported local names and recursive
self references. Exercise its actual creation scope and consumer lifetime.

Recursive declarations use the selected runtime's supported forward-annotation form;
on a floor requiring postponed evaluation, an unquoted self-reference without that
postponement fails before Pydantic can resolve it. Prove a fresh public import and
recursive validation under the actual floor rather than copying an incomplete snippet.

Fix a proven export, dependency or namespace defect at its owner, without rebuild
calls, copied namespace maps or metadata patches. Under FLEXT ADR-018, a local class
retains its runtime class and closure; its generated protocol receives deterministic
lexical qualification. Hoisting or renaming the runtime class is not a namespace fix.
See [native annotation resolution at v2.14.1](https://github.com/pydantic/pydantic/blob/v2.14.1/docs/internals/resolving_annotations.md).

## Project-owned model and service protocol projection

When the project declares automatic structural projection, resolve its accepted,
branch-matched ADR-018 "Model and service protocol projection" contract before
changing generation or consumers. That project decision owns coverage, source-module
grouping, public names, transaction closure and rollout; this procedure does not
declare a competing projection policy.

Account for the complete authenticated Python inventory, not just known consumers
or conventional source directories. Use the existing native semantic model to
distinguish annotation references from constructors, validation, schema, field and
handler metadata, inheritance and DI uses. Preserve their originating runtime
contracts and existing authored ports while projecting first-party declarations;
never mirror an external SDK or turn a protocol into a runtime model.

Apply one admitted pattern through the project's existing generator, native
reference graph and publisher. Profile the real path with cProfile before tuning;
reuse native caches and incremental invalidation rather than adding an index or
scanner. Derive pilot variation coverage from the full inventory and retain real
runtime, invalid-case, consumer-closure and fixed-point evidence. A distant pilot
or a smaller diagnostic count alone does not establish full coverage or repair.
