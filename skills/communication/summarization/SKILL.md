---
name: summarization
description: "Condense documents, conversations, code, and technical content into accurate summaries. USE FOR: 'summarize this', TL;DR, executive summary, key points, meeting notes, changelog digests. DO NOT USE FOR: rewriting/paraphrasing at similar length; translation; generating new content."
license: MIT
metadata:
  bundle: communication
  scope: universal
---

# Summarization

Approach skeletons: [references/approach-templates.md](references/approach-templates.md).

## First

Content type → audience → purpose → target length (scale to complexity, not raw length). Lists are fine here: a summary is inherently list-shaped content (caveman rule 5).

## Structures

- **Executive**: bottom line first, 2–4 critical metrics, findings, risks, next steps.
- **Technical**: purpose, approach, key decisions, dependencies, trade-offs, limitations.
- **Research**: question, method brief, 3–5 findings, significance, limits.
- **Meeting**: decisions, action items with owners+deadlines, disagreements, open questions.
- **Code/changelog**: what changed, why, user impact, breaking changes.

## Principles

- Never introduce what isn't in the source; ambiguity stays flagged as ambiguous.
- Source terminology; exact quotes or preserved intent.
- Most important first (inverted pyramid); related points grouped.
- Preserve numbers, dates, units exactly — "up 23% YoY", never "grew significantly".
- Multi-doc: read all first, synthesize themes, attribute conflicts to sources.

## Checklist

Decision possible from summary alone? All key numbers kept? Nothing not-in-source? Fair to the author? Right length?
