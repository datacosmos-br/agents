# Skill authoring procedure

## Discovery

1. Resolve the active skill authority from the current repository configuration.
2. Search names, descriptions, procedures, catalog policy, and built-in provider
   capabilities for the requested behavior.
3. Extend or compose the existing owner when its contract already covers the
   request. Similar wording is not a distinct capability.

For an external or historical corpus, inspect every relevant bundle together
with its references, scripts, assets, manifest, provenance, license, generated
state, activation, effects, consumers, and failure behavior. Reduce it to a
semantic signature before comparing names. Classify each behavior as already
owned, an extension of one owner, a distinct recurring capability, or rejected
residue. Never import its directory structure, updater, projection, runtime, or
identity as a compatibility alias.

Complete catalog, ownership, capability, path, and validation discovery before
the first bundle write. A missing or conflicting prerequisite stops creation;
never create a provisional identity or local fallback.

## External governance adjudication

Treat an external or historical governance corpus as read-only evidence, never
as a directory or identity to copy. Read each relevant bundle together with its
references, scripts, assets, manifests, provenance, license, generated state,
consumers, executable effects, and failure behavior. Reduce each behavior to its
outcome, trigger, non-trigger, inputs, effects, scope, consumer, and material
proof before selecting an owner.

Classify each surviving statement through this repository's semantic artifact
contract: mandatory invariants belong to rules, conditional procedures to
skills, explicit invocation grammar to commands, and discovery metadata to
agents or config. AI Hub alone maps the published bundle into project runtime
and provider delivery. Extend or compose the current semantic owner when it
already covers the behavior. Create a skill only for an independently recurring
outcome with complete semantic evaluation. Split mixed sources and reject copied
structure, provider assumptions, private paths, foreign runtimes, fallback,
retry, compatibility, partial execution, and behavior without a current
consumer.

Rewire every current consumer and update ownership mapping, semantic suites,
documentation, and the public bundle atomically. Remove each superseded
canonical identity in the same cutover without modifying the supplied source
corpus. Prove the installed bundle and zero duplicate owner, alias, or
stale-consumer residue; AI Hub owns downstream generation and its fixed-point
proof.

## Bundle contract

Create one kebab-case directory containing a compact `SKILL.md` router. Its
frontmatter has the matching name and a short comma-separated list of unique
lowercase discovery terms. Keep routing triggers, non-triggers, invoked owners,
and single-operation guidance in the body; the description is not prose or
provenance.

Keep activation, non-activation, and routing in `SKILL.md`. Put detailed procedure,
examples, schemas, or templates under the same bundle's `references/`, `scripts/`,
or `assets/` directories. Never use a symlink, external repository path, user-home
path, or generated copy as the source of truth.

## Evaluation

Every active skill owns one provider-neutral `suite.yaml` manifest with exactly
three semantic roles:

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

Run `make runtime APPLY=Y` to validate the installed bundle, then
`make check APPLY=Y`, `make test APPLY=Y`, and `make test-full APPLY=Y`. The
official Waza spec verifier is part of the check owner and validates every
projected skill/evaluation pair offline at the exact threshold. Readiness
advisories and live model execution are not semantic authorities. Never invoke
Waza, pytest, or another underlying tool directly. If the skill changes the
public semantic contract, migrate all AI Hub consumers in the same cutover;
AI Hub owns downstream generation.

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
- Mandatory invariants, explicit invocation grammar, and discovery metadata
  remain with rules, commands, agents, and config. Runtime and provider delivery
  remain outside this bundle with AI Hub; split a mixed historical source rather
  than copying those statements here.
