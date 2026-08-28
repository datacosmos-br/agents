# Skills strict-execution plan

## Exclusive objective

Review every current canonical skill and its Waza suite against the central
extermination policies. The original audit covered 76 migrated skills; the
current acceptance set is 78 after two authorized governance additions. This plan owns only `skills/**` and the
`evals/<skill-slug>/**` suites that belong to catalog-discovered skills. It does
not own runtime code, central rules, configuration, documentation, Make, CI,
or `skills.lock.json`.

## Per-skill contract

Read each complete bundle: `SKILL.md`, procedures, references, scripts, assets,
and evals. Then:

1. Add the mandatory `policy:strict-execution` tag.
2. Add every directly applicable policy tag from the central vocabulary.
3. Reference policies by their central tags; never copy the complete rule text.
4. Remove instructions that allow catches, warnings, skips, findings, retries,
   fallbacks, undeclared, competing, or error-triggered defaults, alternate
   providers/models/credentials,
   effects before preflight, partial publication, normalized subprocess failure,
   keyring use, or deferred cleanup.
5. Preserve the capability, activation boundary, should-not-run behavior,
   portability, and provider-independent semantics.
6. Make the three Waza roles prove a material success, the first causal failure
   with zero effects, and adjacent non-activation without fallback.

An apparent need outside the owned paths is reported as a blocker. It does not
authorize a cross-boundary edit.

A deterministic default declared and validated once by the typed SSOT is normal
owner behavior, not fallback. Skills must not demand an equal environment
variable, setting, parameter, or argument from a consumer.

## Batches and evidence

Execute in this order: `agent-wide`, `project-wide`, `technology`, `framework`,
`tool`, and `domain`. For every slug, run the canonical focused check and spec
gate. For every batch, run a semantic residue search and `git diff --check`,
then publish one WIP commit containing only owned paths.

Do not regenerate the inventory lock, fetch, merge, open or update a PR, rebase,
squash, force-push, reset, stash, or invoke Beads, Dolt, Gas City, or Gas Town.
The final handoff consists only of the six pushed SHAs, reviewed slugs, command
evidence, and exact blockers. No skill or phase is declared `DONE`.
