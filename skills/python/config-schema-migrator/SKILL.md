---
name: config-schema-migrator
description: "Evolve Pydantic configuration schemas for shipped products with backward compatibility. USE FOR: adding/restructuring config fields in a DELIVERED product's user-facing config; writing migration scripts for user configs; env-var substitution; discriminated unions for config types. DO NOT USE FOR: internal code refactors (universal law: complete cutover, no old+new — sprint-closure governs); generated projections (regenerate at SSOT instead)."
license: MIT
metadata:
  bundle: python
  scope: universal
---

# Config Schema Migrator

Scope: **user-facing config of shipped products** — where users, not the repo, own the file and need a migration path. Internal refactors follow zero-residue cutover instead.

## Principles

1. New schema version is the only schema in code; old shape exists only in the migration script that transforms user files forward.
2. Validate at load time with Pydantic validators; fail loud with migration instructions.
3. `${VAR_NAME}` substitution for secrets.
4. Discriminated unions (`Field(discriminator=...)`) for variant config types.

## Evolution flow

1. Bump schema at its SSOT; regenerate projections via the project generator — never hand-edit generated output.
2. Extend the model with new fields + validators (`model_post_init` for cross-field rules).
3. Ship `migrate` entry point: load old file → transform → write new → verify round-trip.
4. Release notes carry before/after examples.

## Example

```python
class AdapterConfig(BaseModel):
    type: Literal["cli", "http"]          # discriminator
    timeout: float = 30.0

class Config(BaseModel):
    adapters: dict[str, AdapterConfig]

    @model_validator(mode="after")
    def _check(self):
        if not self.adapters:
            raise ValueError("adapters required; run `tool migrate` to convert legacy cli_tools")
        return self
```

Patterns and longer examples: [references/patterns-source.md](references/patterns-source.md).
