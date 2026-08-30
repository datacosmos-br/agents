---
name: summarization
description: 'source compression, bounded summaries, factual fidelity'
metadata:
  aihub.tags: '["policy:fail-loud","policy:no-fallback","policy:preflight-before-effects","policy:strict-execution","provenance:agents-owned","role:writing","updates:manual","usage:on-demand"]'
  version: 3.0.0
---

# Summarization

Compress supplied material without changing facts, attribution, uncertainty, or
decision context. Select the audience-specific structure from
`approach templates` (skill file).

## Contract

1. Establish audience, purpose, source set, and requested length.
2. Lead with the decision, result, or conclusion the reader needs.
3. Preserve decisive numbers, units, dates, owners, interfaces, limitations,
   disagreements, and open questions.
4. Distinguish source statements, inference, correlation, and causation.
5. Remove repetition and supporting detail that does not change understanding or
   action; never invent missing content.
6. For multiple sources, reconcile agreement and conflict with attribution instead
   of flattening them into a false consensus.

Missing, inaccessible, empty, or conflicting required source material blocks a
factual summary before writing begins. Name the first causal defect and produce
no partial summary, inferred replacement, generic template, or alternate source.
