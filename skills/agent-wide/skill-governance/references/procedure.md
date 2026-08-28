# Skill authoring procedure

## Discovery

1. Resolve the active skill authority from the current repository configuration.
2. Search names, descriptions, procedures, catalog policy, and built-in provider
   capabilities for the requested behavior.
3. Extend or compose the existing owner when its contract already covers the
   request. Similar wording is not a distinct capability.

Complete catalog, ownership, capability, path, and validation discovery before
the first bundle write. A missing or conflicting prerequisite stops creation;
never create a provisional identity or local fallback.

## Bundle contract

Create one kebab-case directory containing a compact `SKILL.md` router. Its
frontmatter has the matching name and a short comma-separated keyword list;
descriptions are discovery metadata, never prose or provenance.

Keep activation, non-activation, and routing in `SKILL.md`. Put detailed procedure,
examples, schemas, or templates under the same bundle's `references/`, `scripts/`,
or `assets/` directories. Never use a symlink, external repository path, user-home
path, or generated copy as the source of truth.

## Evaluation

Every active skill owns one Waza suite with exactly three semantic roles:

- a realistic happy path using a domain-specific regular fixture;
- a genuinely missing or ambiguous input that fails closed;
- a unique adjacent request that must not trigger the skill.

Use material artifact or outcome assertions, a skill-specific prompt grader, and
a behavior duration strictly below executor timeout. Task IDs and prompts are
globally unique. A generic fixture, copied frontmatter prompt, non-empty “empty”
case, or `task_completed` without proof is invalid.

Create or update the router, supporting resources, and all three semantic eval
roles as one atomic bundle change. Do not publish a router with partial evals.

## Validation

Run the repository's canonical skill validator, official Waza spec coverage gate,
focused tests, and projection fixed-point check. If the new skill changes a public
catalog or projection contract, regenerate through its owner and migrate all
consumers in the same change.

Before adding, removing, or renaming a skill, search migration maps, category
lists, numeric acceptance criteria, fixtures, docs, generated inventories, and CI
contracts. Update every current-count owner atomically with the bundle and lock,
while preserving historical command output as history. A catalog count that
differs from an active acceptance contract is a blocking defect, not an external
addition or documentation follow-up.

The first causal gate failure stops that validation invocation. Correct the
bundle owner and rerun every invalidated gate before publishing; never repeat an
unchanged command, substitute a gate, publish partial evidence, or hand off a
failed scaffold. Require zero duplicate identity, compatibility router,
placeholder, and superseded consumer residue.

## Boundaries

- One tight behavior class per skill; no duplicate, alias, compatibility router,
  or imported identity.
- Generic project skills contain no private workflow, tracker, home path, or
  cross-repository contract.
- Technology skills are distributed only after structured project detection and
  never as personal capabilities.
- Personal skills contain non-technological operator workflows and capabilities.
