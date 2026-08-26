# Living Documentation (worker reference)

Adopted with provenance from the ccs-era universal stack
(`agentes-legacy/.agents/workflows/docs.md` + `commands/update-docs.md`),
per UNIVERSAL_CORE 11/14. Historical source is evidence; this is the live rule.

## The Rule

Docs that a change makes necessary ship **in the same change** (same bead,
same PR). Stale docs are defects: file a bead, never work around them.

## On Entering A Project (never rebuild from zero)

1. Read the project's docs FIRST: root `AGENTS.md`, `docs/` (PATTERNS/
   CODING-STANDARD/RUNBOOK/ADRs), project skill under `skills/`.
2. Validate a few key claims quickly against live reality (a command, a
   file:line, a running surface) before trusting them — docs lie by
   omission, reality never does.
3. Record what you learned by UPDATING the doc that should have told you:
   fix the stale line, add the missing fact, in the same change that
   produced the understanding. Do not carry rediscovery in your head or in
   session notes.

## Sync From Source Of Truth (update-docs pattern)

| Source | Generates |
|---|---|
| `Makefile`/`pyproject.toml`/scripts | command reference |
| config schemas / `.env.example` | configuration docs |
| route/OpenAPI files | endpoint reference |
| public exports / facades | API docs |

Regenerate the reference from the source; hand-edit only prose. Verify
links and that code examples in docs still run.

## Merge-Ready Slice Discipline (UNIVERSAL_CORE 13)

One bead = one reviewable PR, independently green, mergeable within a
session. If your lane cannot reach a validated, reviewable state in a
session, it is too big — file the split and land the first slice.
