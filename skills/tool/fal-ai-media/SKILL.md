---
name: fal-ai-media
description: "fal.ai, media generation, external service"
metadata:
  aihub.tags: '["activation:opt-in","decision:ADR-0008","detect:opt-in:fal-ai","effective:2026-08-28","route:agent","subject:fal-ai","usage:on-demand"]'
---

# fal.ai Media Generation

Activate only for an explicit fal.ai image, video, or audio generation/edit. Metadata
inspection or media work assigned to another owner does not activate it.

Before upload or generation, resolve the exact prompt and inputs, requested medium and
parameters, current fal.ai MCP interface, model catalog and schemas, one
capability-matching model, cost estimate, spending approval, content and effect
authorization, required current-process credential, timeout, and final artifact
destination. Reject any missing, invalid, conflicting, or unexpanded requirement before
the first effect.

Use exactly the model and schema selected from current owner evidence. Never use
keyring, profiles, credential files, copied model recommendations, operational defaults,
alternate providers or models, parameter substitution, or prompt rewriting. Submit once.
A returned asynchronous job remains the same causal job; observe only that identity to
its declared terminal boundary and never resubmit.

The first upload, estimate, approval, generation, status, timeout, signal, or download
failure propagates unchanged. Do not retry or publish partial media. Validate the
returned medium and requested properties before atomically publishing it at the declared
destination. Cleanup may attach a secondary failure but must re-raise the first cause
and remove all partial artifacts.

Report only observed job and artifact evidence; never invent completion or URL.
