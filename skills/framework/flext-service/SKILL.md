---
name: flext-service
description:
  "flext service composition, service base kernel, classmethod handlers, protocol
  injection"
metadata:
  aihub.tags: '["activation:detected","decision:ADR-0014","detect:dependency:python:flext-core","detect:selected-tag:flext","effective:2026-09-17","extends:flext-development","route:project","subject:flext","usage:on-demand"]'
---

# FLEXT Service Composition

Activate for a detected internal FLEXT consumer when creating or reshaping a domain
service: deciding service versus utility versus model behavior, the project service base
and its `s` facade alias, classmethod or staticmethod handlers that return results,
protocol-injected collaborators, or the api composition root. Do not activate for Result
operation selection (`$flext-result`), settings or config lifecycle (`$flext-config`),
family part layout law (`$flext-family-shape`), or plain non-FLEXT Python classes.

Load `$flext-development` and its ancestors first; this child owns only the
service-layer delta. Read [the service procedure](references/procedure.md), then verify
the target package's real `base.py`, `p` protocols, services modules, and `api.py`
before edits. Every services class ends its MRO at the project service base, keeps
public boundaries typed over models, protocols, and results, receives collaborators
through constructor or protocol parameters, and hides no singleton, module state, or
environment read. The api composition root stays a pure facade with exactly one eager
alias.
