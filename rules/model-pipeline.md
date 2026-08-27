# Model pipeline

`config/model-pipeline.json` is the sole model-selection contract in this
repository. It resolves to the stable generated alias `ai-hub-primary`.

- Consumers use the alias exactly; they never name a provider model, family,
  tier, variant, effort level, or fallback.
- Caller overrides are forbidden. `MODEL=`, equivalent environment overrides,
  and Waza defaults outside the generated projection must fail closed.
- `agentsctl model-pipeline apply` is the only writer for repository model
  projections. A second application must produce zero changes.
- `agentsctl model-pipeline probe` must find the exact alias in the injected
  provider's model inventory. Absence, authentication failure, quota failure,
  timeout, and transport failure stay red.
- Skill `agents/openai.yaml` files contain only supported interface,
  dependencies, and policy metadata. Model selection does not belong there.

The upstream pipeline may change its concrete implementation without requiring
repository edits. This repository neither knows nor reconstructs that mapping.
