---
name: anti-hardcode
description: 'configuration ownership, portable policy, hardcode removal'
license: MIT
metadata:
  aihub.tags: '["provenance:agents-owned","role:configuration","updates:manual","usage:router"]'
  version: 1.0.0
---

# Anti Hardcode

Operational hardcodes are critical runtime hazards. They can target the wrong
model, provider, endpoint, credential, database, branch, path, environment, or
policy; expose secrets; corrupt state; and lose or duplicate data. They must
never be introduced or retained, and one confirmed occurrence blocks delivery.

Activate for embedded operational values, ad hoc environment reads, duplicated
defaults, magic deployment decisions, or generated copies that do not derive
from the declared configuration owner.

Read the [complete procedure](references/procedure.md). Missing configuration
must fail loudly through a typed error and owning CLI nonzero exit, or be exposed
as an unresolved warning or blocker in the agent's final response.

Do not trigger for a named mathematical, protocol, format, or domain invariant
whose authority and tests prove it is not operator- or environment-controlled.
