# ADR-0002 — Derive skill semantics from paths and tags

- **Status:** Accepted
- **Date:** 2026-08-27
- **Scope:** Skill identity, classification, discovery, and validation

## Context

A separate skill registry can disagree with the physical source tree. Subject,
dependency, activation, and intended route are orthogonal and cannot be encoded reliably
by one flat bucket.

## Decision

The recursive directories `agent-wide`, `project-wide`, `technology`, `framework`,
`tool`, and `domain` own each skill's primary semantic group. Validated frontmatter tags
own orthogonal route, activation, detector, subject, usage, and risk semantics. No
registry lists skill names or categories, and there is exactly one provider-neutral
evaluation suite for every physical skill.

This package describes route and detection semantics but does not discover a consumer's
projects, inspect their environment, select deployment targets, or publish files. AI Hub
applies those semantics to its current typed project and provider inventory.

## Consequences

Recursive discovery is the inventory authority. Unknown, contradictory, colliding,
detectorless, or unevaluated skills fail during `GovernanceBundle.load()`. Distribution
policy can change at the AI Hub boundary without adding a projector or project-local
source owner here.
