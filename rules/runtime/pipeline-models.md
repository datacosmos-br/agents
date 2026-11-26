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
through the pipeline. Recorded evidence (captured logs, fixtures that replay them, dated
plans) may quote an identifier it observed; it never selects one.

AI Hub publishes directly to the serving proxy and projects agent configuration only
after runtime readback confirms the generation. The proxy serves it and owns account
operations. Management interfaces do not publish or replace the generation.

Pipeline probing never spends a provider's quota faster than its declared budget:
evidence is reused until the inventory or a credential changes, route health comes
from the proxy's own quota and cooldown signals, and a probe is one minimal request
per model, protocol and quota domain. No fast, priority or service-tier option is
projected to any agent, and a free tier serves only the agent its provider names.
Each consuming agent receives dedicated routes on both the OpenAI and Anthropic
protocols, and every consumer, including tests and memory servers, names a route from
configuration, never the real model. A shared local model serves only the consumers
the operator names, through the proxy, with its rate and threads declared in
configuration. While the operator's temporary free-tier ruling stands, the proxy
admits only free-tier models from free accounts.
