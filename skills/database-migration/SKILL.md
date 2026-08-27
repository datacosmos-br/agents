---
name: database-migration
description: database, migration, schema, rollback, data, compatibility, validation
---

# Database Migration

Use this workflow for project-owned database schema and data migrations.

## Goal

Change a database safely with reversible migration files and validated consumers.

## Common Files

- `**/schema.*`
- `migrations/*`

## Suggested Sequence

1. Understand the current state and failure mode before editing.
2. Make the smallest coherent change that satisfies the workflow goal.
3. Run the most relevant verification for touched files.
4. Summarize what changed and what still needs review.

## Typical Commit Signals

- Create migration file
- Update schema definitions
- Generate/update types

## Notes

- Treat this as a scaffold, not a hard-coded script.
- Update the command if the workflow evolves materially.
