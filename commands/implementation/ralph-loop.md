---
name: ralph-loop
description:
  Run one bounded delivery iteration through owner correction, runtime, gates, and
  landing.
argument-hint: "<one authorized objective and its acceptance boundary>"
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-08-29","route:project"]'
---

# Bounded delivery loop

Treat `$ARGUMENTS` as one authorized objective and acceptance boundary. Resolve missing
facts through current sources before asking about a non-derivable decision. Preserve
prior exact authorization and the current unit across interruption.
Do not implement an empty, unrelated multi-objective or ownerless unit. An authorized
program may contain several units; select its next bounded unit without discarding
the program or asking for authorization already given.

1. Read the active contract, canonical owner, implementation, consumers, selected
   tracker, integration state and public runtime. Adopt compatible existing work.
2. Select one owner-level correction and the complete consumer closure it requires.
   Keep the current authorization boundary explicit; do not add unrelated repairs or
   a second execution mechanism.
3. Implement through that owner, rewire every affected consumer and remove the
   superseded path. Update documentation and generated artifacts through their owners.
4. Exercise public behavior, then apply `$make-check` and the repository's required
   gates. Command deadlines, profiling, test selection and result classification have
   one owner: `rules/workflow/canonical-commands.md`.
5. Review and integrate the validated candidate through the current Git/PR contract.
   Record source validation, required review, CI, integrated SHA and applicable runtime
   delivery separately. Keep an unavailable required proof open without a substitute
   ledger or an invented success.
6. Begin the next independent unit only after the current unit's acceptance boundary
   is satisfied. A failure is corrected at its owner within authorized scope; any
   genuinely external or newly unauthorized action is identified precisely.

Return the objective, source and consumer changes, removed residue, commands and
exits, integration state and the next eligible action. A branch-only result is a
checkpoint, never completed delivery.
