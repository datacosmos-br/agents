---
description: Agents use only pipeline-propagated models; routing serves what providers serve; no hardcoded model lists
metadata:
  aihub.tags: '["decision:ADR-0038","effective:2026-11-03","route:both"]'
---

# Pipeline models

An agent, surface or projection selects a model only from the generation the model
pipeline published; nothing names a model the pipeline did not propagate. The routing
consumer routes exactly the models the configured providers serve now: a served model is
resolved and routed, never dropped because a catalog does not describe it, and a model a
provider stops serving leaves routing in the next generation. No code, configuration,
template, test or document holds a hardcoded list, default or prefix table of model
identifiers; model identity and selection come only from the providers' live inventory
through the pipeline.
