---
name: data-modeling
description: "data models, model composition, field ownership"
metadata:
  aihub.tags: '["decision:ADR-0038","effective:2026-11-03","supersedes:skill:data-modeling-analysis","usage:on-demand"]'
---

# Data Modeling

Models compose by inheritance and composition. Each field is declared once, at the model
that owns its meaning; a model that extends another never repeats an inherited field,
shared shapes become one base or one composed part, and one domain has one model family.
The result has fewer models, no duplicated data and no repeated domain, and anything
derived from the models (a protocol mirror, a schema, a form) follows the same hierarchy.

1. Read the models, their consumers and their serialized shapes through the project's
   native tools, and group the fields that repeat across models.
2. Move each repeated group to the one base or part that owns it, delete the copies, and
   rewire every consumer in the same change.
3. Keep validation at the external boundary, with the project's typed owner.
4. Prove that the real consumers still read and write the same data, then that a second
   generation of any derived surface changes nothing.

Apply it first where the shape is violated, then across the codebase. Never add a
parallel schema owner, a generic catch-all model or an unsafe deserializer.
