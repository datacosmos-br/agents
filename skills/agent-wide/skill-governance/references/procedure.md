# Skill authoring procedure

## Discovery

1. Resolve the active skill authority from the current repository configuration.
2. Search names, descriptions, procedures, catalog policy, and built-in provider
   capabilities for the requested behavior.
3. Extend or compose the existing owner when its contract already covers the
   request. Similar wording is not a distinct capability.

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

## Validation

Run the repository's canonical skill validator, official Waza spec coverage gate,
focused tests, and projection fixed-point check. If the new skill changes a public
catalog or projection contract, regenerate through its owner and migrate all
consumers in the same change.

## Boundaries

- One tight behavior class per skill; no duplicate, alias, compatibility router,
  or imported identity.
- Generic project skills contain no private workflow, tracker, home path, or
  cross-repository contract.
- Technology skills are distributed only after structured project detection and
  never as personal capabilities.
- Personal skills contain non-technological operator workflows and capabilities.
