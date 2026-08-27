---
name: feature-development
description: feature, development, implementation, tests, interfaces, consumers, documentation, validation
---

# Feature Development

Use this workflow to implement a project feature through its canonical owners and gates.

## Goal

Deliver a coherent feature with affected consumers, tests, documentation, and validation.

## Common Files

- `manifests/*`
- `schemas/*`
- `**/*.test.*`
- `**/api/**`

## Suggested Sequence

1. Understand the current state and failure mode before editing.
2. Make the smallest coherent change that satisfies the workflow goal.
3. Run the most relevant verification for touched files.
4. Summarize what changed and what still needs review.

## Typical Commit Signals

- Add feature implementation
- Add tests for feature
- Update documentation

## Notes

- Treat this as a scaffold, not a hard-coded script.
- Update the command if the workflow evolves materially.
