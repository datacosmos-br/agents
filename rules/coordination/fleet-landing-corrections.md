---
description:
  Fleet landing cycles follow root cause, tag-line authority, canonical commands,
  integration closure, and unmasked validation.
capsule_summary: |
  Fleet landing: suppress no warning without removing the duplication that
  caused it; version lines follow the declared tag timeline; commands execute
  only from canonical docs plus measured evidence; a cycle closes only with a
  no-ff merge on the integration lane, verified deploy, lane retirement, and
  bead evidence; pipelines never mask a producer's exit code.
metadata:
  aihub.tags: '["decision:ADR-0011","effective:2026-09-10","route:personal"]'
---

# Operator corrections — fleet landing cycles (2026-09-08/10)

High-authority corrections with a declared scope, drawn from the landing cycles of the
`~/gc` city. Scope: landing and integration operations on fleet rigs. Do not generalize
them to other domains without a new order.

1. **Root cause, never the messenger.** Suppressing a warning (for example
   `shadow = "silent"`) without removing the duplication that produced it is a
   violation. The fix removes the cause; the warning disappears as a consequence.
2. **Version line: the tag and release timeline is the authority.** Never invent or
   adopt identities of discontinued lines; before a bump, read the tags (for example
   dc3→fd1→fd2→fd3) and follow the live line the operator declared.
3. **A command without a canonical basis does not run.** Every action starts from the
   project's official docs and skills and from measured evidence (command, cwd, exit,
   decisive output). Guessing a flag, a command, or a semantic is a violation.
4. **The cycle closes on the integration branch.** Delivery without a no-ff merge on the
   integration lane plus a verified deploy is not delivery: lane → PR → correction →
   no-ff merge → lane, branch, and worktree retirement → bead closed with evidence.
5. **Validation never masks the producer.** Pipelines (`wc`, `grep`, `tail` after a
   command) do not replace the producer's exit code; a producer failure invalidates the
   PASS. Suite claims (for example "12/12") that masked a failure are withdrawn with an
   explicit correction on the bead.
