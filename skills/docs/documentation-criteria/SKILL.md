---
name: documentation-criteria
description: "Which technical documents a change requires (PRD, ADR, UI Spec, Design Doc, Work Plan) and in what order. USE FOR: deciding required docs before implementing; reviewing doc completeness; locating templates. DO NOT USE FOR: prose style (writing-style); doc drift execution (doc-drift); tracker items (beads)."
license: MIT
metadata:
  bundle: docs
  scope: universal
---

# Documentation Criteria

Templates: [references/](references/) · detailed definitions: [document-definitions.md](references/document-definitions.md).

## Decision matrix

| Condition | Required docs | Order |
|---|---|---|
| New feature backend | PRD → [ADR] → Design Doc → Work Plan | after PRD approval |
| New feature frontend/fullstack | PRD → UI Spec → [ADR] → Design Doc → Work Plan | UI Spec before Design |
| ADR condition met (below) | ADR → Design Doc → Work Plan | immediately |
| 6+ files | ADR + Design Doc + Work Plan | immediately |
| 3–5 files | Design Doc + Work Plan (recommended) | immediately |
| 1–2 files | none | direct implementation |

## ADR mandatory when

- Contract nesting 3+ levels; contract used in 3+ places changed/removed; responsibility shift (DTO→Entity).
- Storage location change; processing order 3+ steps; parameter→shared-state passing change.
- Layer addition/responsibility move; new library/framework/external API.
- Complex logic regardless of size: 3+ states or 5+ async processes coordinated.

## Document scopes

- **PRD**: value, metrics, stories, ACs · **UI Spec**: screens, state matrices, traceability; prototype = attachment
- **ADR**: decision + ≥3 options compared · **Design Doc**: impact map, interfaces, verification strategy
- **Work Plan**: tasks ≤2 levels, QA phase last

## Process

Scale + ADR check → options compared → measurable docs → "Accepted" unlocks work. Storage: `docs/{prd,ui-spec,adr,design,plans}/`.
