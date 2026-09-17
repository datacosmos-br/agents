# FLEXT service composition procedure

Ground every rule in the target package's real source before editing: the
framework service kernel (`flext_core.service`), the project `base.py`, its
`p` protocols family, its services modules, and its `api.py` root. Never
invent a facade, base class, or protocol the package does not declare.

## 1. Classify the owner first

- **Model** (`m.*`, `_models/`): fields, `model_config`, validators,
  `computed_field` only. A `get_*` / `to_*` / `from_*` / `is_*` / `with_*`
  helper on a data model is a defect; relocate it to a service or a
  `@computed_field` (ENFORCE-058).
- **Utility**: stateless owner of `@classmethod` / `@staticmethod` members
  only; no instance state, no lifecycle, never a singleton. Example:
  `AiHubWorkspaceConfig` in
  `src/ai_hub/services/generate_workspace_config.py` (`plan`, `verify`).
- **Service**: a class whose MRO ends at the project service base —
  `Flext<X>ServiceBase` inheriting `FlextService` (`s[T]` from
  `flext_core`) — owning one domain operation that returns a typed result
  (ENFORCE-057). It may hold injected collaborators and per-instance state.

An operation with runtime effects or multi-step composition is a service; a
pure transformation is a utility or model; behavior attached to a model is a
smell until relocated.

## 2. The `s` facade import convention

`flext_core.service` exports `FlextService` with alias `s`. Each consumer
package declares exactly one service base in its root `base.py` and
publishes the local alias every service imports:

```python
# src/ai_hub/base.py (real consumer)
from flext_core import r, s as _flext_service

class AiHubServiceBase(_flext_service[t.JsonMapping], ABC): ...
s = AiHubServiceBase
```

Services bind the project base, never the framework base directly:

```python
from ai_hub import m, p, r, s

class AiHubDeployService(s): ...
```

Importing `flext_core.s` from a leaf service module is a defect: it bypasses
the project settings binding and duplicates the base. The local `s` alias is
the single import surface (`from <package> import s`).

## 3. Handlers return results; registries are immutable and fail closed

- Operations and stateless handlers return `p.Result[...]` (built through
  the package `r[T]` alias), never raise for expected domain failure, never
  return bare `bool`, `dict`, or `None`.
- Handler tables are class-level immutable mappings typed by constants
  enums, resolved by one classmethod that fails closed on an unknown key:

```python
# src/ai_hub/services/_deploy_agents_parts/surfaces.py (abridged)
class AiHubDeploySurfaces(AiHubDeployReceipts):
    ADAPTERS: MappingProxyType[...] = MappingProxyType({
        (c.AiHub.SurfaceType.HOOKS, "json"): AiHubDeployHooksJson, ...})

    @classmethod
    def adapter_for(cls, surface, home) -> p.Result[p.AiHub.SurfaceAdapter]:
        factory = cls.ADAPTERS.get((surface.surface_type, surface.format))
        if factory is None:
            return r[p.AiHub.SurfaceAdapter].fail(f"no deploy adapter for surface")
        return r[p.AiHub.SurfaceAdapter].ok(factory(home))
```

- Public parameters and returns in services modules and `api.py` are
  Pydantic models (`m.*`), `p.*` protocols, `r[T]` of those, or PEP 604
  unions — never bare `dict`, `list[primitive]`, `set`, `TypedDict`
  (ENFORCE-059).

## 4. Dependency injection through `p` protocols, wired at the api root

- Cross-cutting collaborators are `p.*` protocols declared once in the
  project protocols family, for example `p.AiHub.DeploymentAcceptance` (a
  runtime-checkable callable protocol) and `p.AiHub.SurfaceAdapter`.
- Services accept protocols as keyword-only parameters. An optional protocol
  parameter defaults to `None`, and `None` fails closed with a typed failure
  naming the requirement — never a silent default implementation:

```python
# src/ai_hub/services/deploy_agents.py (abridged)
def execute(self, params: p.AiHub.DeployAgentsInput, *,
            accept: p.AiHub.DeploymentAcceptance | None = None) -> p.Result[bool]:
    if accept is None:
        return r[bool].fail("deployment requires an isolated native acceptance provider")
```

- Concrete peer services are constructor-injected with explicit typed
  parameters; see `FlextAuthApplicationService.__init__` in the flext-auth
  family package (settings, registry, dispatcher, sibling services).
- The api root is the only composition point: one pass-only facade class
  composing the service mixins through MRO (`class AiHub(...services)`,
  `ai_hub: AiHub = AiHub.fetch_global()`), no domain method, no
  module-level mutable instance (ENFORCE-065).

## 5. No hidden state, singletons, or environment reads inside services

- The singleton kernel — `fetch_global()`, `reset_for_testing()`,
  `with_settings()` — is inherited from the framework base, once per
  concrete class. A project base inherits it; a domain service never
  redeclares or hand-rolls a singleton accessor (ENFORCE-057). ENFORCE-058's
  factory-kernel carve-out covers only infrastructure bases
  (`FlextService`, `FlextSettings`, the project service base).
- Settings arrive through an injected snapshot (`with_settings(...)`, a
  constructor parameter) or the package's pre-instantiated `settings` /
  `config` singletons. `os.environ` and `os.getenv` in package source are
  defects (ENFORCE-037).
- Module-level mutable instances are forbidden; the only eager instantiation
  is the composition-root alias. Test isolation uses
  `reset_for_testing()`, not ad-hoc module surgery.

## 6. Family part shape for service parts

The public service class lives in `services/<owner>.py`. When its body
grows, split behavior into part classes under
`services/_<owner>_parts/<part>.py` — one part class per file, chained by
inheritance, entities nested flat per `$flext-family-shape`:```text
services/deploy_agents.py                   class AiHubDeploy(AiHubDeploySurfaces)
services/_deploy_agents_parts/surfaces.py   class AiHubDeploySurfaces(AiHubDeployReceipts)
services/_deploy_agents_parts/receipts.py   class AiHubDeployReceipts(...)
```

Parts carry the domain behavior; the public class stays the composition
head and the only name consumers import.

## 7. Before and after from real consumers

### 7.1 Publishing the local `s` alias (`src/ai_hub/base.py`)

Before: a migration moved services to `class X(s)` while the package had
not published a local alias, so leaf modules imported the framework base
directly and the migration half-resolved.

After (current source): the root `base.py` imports
`from flext_core import s as _flext_service`, binds the project settings
type, overrides `execute`, and publishes `s = AiHubServiceBase`; every
service imports only `from ai_hub import s`.

### 7.2 Moving a domain method out of the composition root (`src/ai_hub/services/deploy.py`)

Before: the facade root inlined the workspace-coverage preflight, so the
api root carried domain logic and facade purity failed.

After (current source): the deployment owner sequences its own preflight:

```python
class AiHubDeployService(s):
    @staticmethod
    def _require_workspace_coverage() -> p.Result[bool]:
        return AiHubWorkspaceDiscoveryService().workspace_discovery(
            m.AiHub.WorkspaceDiscoveryInput(audit=True))

    def deploy_agents(self, params: p.AiHub.DeployAgentsInput) -> p.Result[bool]:
        coverage = self._require_workspace_coverage()
        if coverage.failure:
            return coverage
        return AiHubDeploy().execute(params, accept=self._accept_deployment)
```

### 7.3 A registry replaces ad-hoc dispatch (`_deploy_agents_parts/surfaces.py`)

Before: surface rendering branched per `(surface_type, format)` at each
call site, duplicating failure handling and drifting between surfaces.

After (current source): the immutable `ADAPTERS` mapping plus the
`adapter_for` classmethod of section 3 — one fail-closed resolution point
typed by `c.AiHub.SurfaceType`, returning
`p.Result[p.AiHub.SurfaceAdapter]`.

## 8. Verify

Prove changed services through the package's public runtime and native
gates; never widen a boundary type or mute an enforcement warning.
