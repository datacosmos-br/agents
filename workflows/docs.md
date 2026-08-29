# Workflow: documentation

## Goal

Make active documentation match the current runtime, interfaces, ownership, and
delivery law without duplicating canonical procedures.

Documentation-only drift fixes are valid changes; they do not require an
unrelated code change first.

## Procedure

1. Read repository law and identify the canonical code, configuration, schema,
   CLI help, or pinned upstream source for every changed claim.
2. Inventory commands, flags, paths, model names, generated surfaces, PR facts,
   integration branches, and status language in the affected documents.
3. Reproduce local help or read the owning parser/configuration. Never invent a
   flag or infer behavior from stale examples.
4. Replace stale active guidance at the owner. Preserve useful history only when
   it is explicitly marked non-executable and cannot be mistaken for current
   instruction.
5. Prefer a link to a local canonical document over duplicated prose.
6. Keep examples portable: no private absolute paths, symlinks,
   cross-repository references, embedded secrets, or project-specific defaults
   in generic/projected content.
7. Validate local Markdown links, contradiction searches, formatting, and every
   repository-native documentation gate.
8. Review `git diff --check` and the exact documentation diff.
9. Follow the landing contract in [WORKFLOWS.md](WORKFLOWS.md).

## Acceptance

Commands and flags match current owners; active links resolve; historical facts
are labeled; project projection is limited to generic, detected-technology, and
conditional FLEXT content; closure language requires both merged integration PR
and canonical tracker closure.

While tracker runtime is suspended, create no substitute tracker or ledger, preserve
documentation evidence only in separately authorized Git/PR/CI, and leave phase
closure open.
