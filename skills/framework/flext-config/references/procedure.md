# FLEXT settings/config ownership procedure

Grounded in `flext-core` `_settings.py`, `_config.py`, `_protocols/settings.py`,
`_protocols/config.py`, `_utilities/settings.py`, `_utilities/config.py`,
`_constants/settings.py`, `_constants/config.py`, `_models/settings.py`,
`_models/config.py`, and real consumer usage: `ai_hub/_settings.py`,
`ai_hub/_settings_root.py`, `ai_hub/_config.py`, `ai_hub/_utilities/config.py`,
and `tests/unit/test_aihub_config_env_seam.py`.

## Ownership contract

- `FlextSettings` (pydantic `BaseSettings`) owns EXTERNAL INPUTS: environment
  variables through `env_prefix`, `.env` discovery through `FLEXT_ENV_FILE`
  (`resolve_env_file`), and nested settings sources. Mutable per-class
  singleton: `fetch_global`, `update_global` (pure `model_copy(update=...)`
  plus revalidation), `clone`, `reset_for_testing`. Exported as
  `settings = FlextXSettings.fetch_global()`.
- `FlextConfig` (sibling base, flext ADR-005) owns GOVERNED DECLARATIVE RULES:
  every `config/*.yaml` auto-discovered and deep-merged (governed files carry
  the `AiHub:` envelope; lists concatenate, never replace), validated into one
  frozen Pydantic root at first `fetch_global()`. Read-only: no `update_global`
  exists. Exported as `config = FlextXConfig.fetch_global()`.
- Siblings, never nested: neither exposes the other; both stay layer-0 pure
  (stdlib + pydantic-settings only, no facade imports). Projects subclass both
  (`AiHubSettings(AiHubSettingsRoot, AiHubSettingsSources, FlextSettings)`,
  `AiHubConfig(AiHubSettingsSources, FlextConfig)`) and nest every knob under
  one envelope. Strict access: `settings.AiHub.<domain>` and
  `config.AiHub.<domain>` - no flat fields, no compatibility aliases.

## Decision law

1. A value that varies per process or deployment (operator env, credential
   alias, timeout) is a typed settings field; pydantic-settings coercion is the
   validation.
2. A rule that ships with the code (registry, policy, product law) is a
   governed YAML file under `config/` typed by a frozen config model.
3. A value derived from another owned value (a path under `state_dir`) is a
   computed field or a `model_post_init` rebind from the one owner. The
   consumer's `placeholder_runtime_dir` mirrors the owner's absent-`XDG_RUNTIME_DIR` shape
   and `model_post_init` rebinds every derived path from the `FlextSettings`
   `state_dir`/`runtime_dir` owner; a placeholder that once carried its own
   fallback froze a daemon socket because two answers to one question existed.

## Expansion placeholders

- Grammar `${VAR}` and `${VAR:-default}`, expanded once at the YAML source
  (`AiHubConfigEnv.expand_env`; flext-core `u.Config.config_env_override`)
  recursively over string leaves, bounded passes, fixed point required.
- No-residue law: a `${...}` still present after expansion raises `ValueError`
  (a misspelled name never matches the grammar and would ship as a literal
  path); an undeclared name without a default raises instead of resolving to an
  empty path component.
- Verbatim domains (`skip_keys`, e.g. agents/proxy/models/products) keep
  `${AI_HUB_HOME}` literal at load; the owning renderer expands later through
  `expand_text` with its own closed table.
- The expansion env is typed defaults, then `os.environ`, then derived roots
  (`AI_HUB_BUILD`, `AI_HUB_VENV`); derived roots are named by their owners and
  always win.

## Service consumption law

Services consume settings/config only through explicit parameters or the
validated global facade (`settings.AiHub.<domain>`, `config.AiHub.<domain>`).
Never `os.environ`, `Path.home()`, `os.getcwd()`, or a re-parsed YAML file in a
service: each is a second, unvalidated answer beside the singleton, invisible
to `reset_for_testing` repointing. `config.AiHub` is a validated frozen model,
not a `Result`: validation happened exactly once at load and consumers trust
typed attributes. Result wrapping belongs at operation boundaries - service
methods return `p.Result[T]` and wrap failure there, never around config
attribute access.

## Test repoint pattern

Repoint through the production env seam, never by patching: set
`AI_HUB_CONFIG_DIR` in a real `os.environ` context manager, call
`AiHubConfig.reset_for_testing()` (the bound singleton revalidates in place so
every importer handle stays live), restore the env and reset again in
`finally`. Settings repoints the same way through its `AI_HUB_*` env channel
(`FLEXT_ENV_FILE`, `AI_HUB_STATE_DIR`, namespace `<NAME>_DIR` overrides). No
`monkeypatch`, no `CONFIG_DIR` ClassVar edit, no module-attribute freeze.

## Examples

### 1. Service reading process globals - before/after

Before (defect: unvalidated second answer, invisible to repointing):

    def carrier_root(self) -> Path:
        root = os.environ.get("AI_HUB_CARRIERS_ROOT")
        return Path(root) if root else Path.home() / ".carriers"

After (one owner, typed, repointable through the settings facade):

    # AiHubSettingsModels.Root declares the field once; the settings root
    # rebuilds it from the Flext dir owner in model_post_init.
    def carrier_root(self) -> Path:
        return settings.AiHub.paths.carriers_root

### 2. Test patching the config owner - before/after

Before (defect: exercises a seam production never uses; importers go stale):

    monkeypatch.setattr(AiHubConfig, "CONFIG_DIR", str(cfg_dir))

After (the real seam, from test_aihub_config_env_seam.py):

    os.environ["AI_HUB_CONFIG_DIR"] = str(cfg_dir)
    AiHubConfig.reset_for_testing()
    try:
        assert config.AiHub.models.cycle.interval_seconds == 601
    finally:
        os.environ.pop("AI_HUB_CONFIG_DIR", None)
        AiHubConfig.reset_for_testing()

### Anti-example - process globals in a service

    class ShipmentService:
        def dispatch(self, order: Order) -> p.Result[Receipt]:
            token = os.environ["CARRIER_TOKEN"]          # unvalidated env read
            home = Path.home()                            # second home answer
            state = home / ".local" / "state" / "orders"  # shadows settings state_dir
            ...

Why it fails: the service owns a private, untyped configuration channel - no
coercion, no repoint, no singleton consistency; `state` silently disagrees with
`settings.state_dir`, and a hermetic `AI_HUB_STATE_DIR` test run writes to the
real home. The owner-correct form takes `settings.AiHub` (or its fields) as
explicit parameters or reads the validated facade, and derives state under the
owned `state_dir`. Real consumers follow this: deployment parts read
`config.AiHub.products.products.entries`, MCP doctor reads
`config.AiHub.agents.agents.items()`.
