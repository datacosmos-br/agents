---
description:
  Editing canonical governance rules, skills, commands, evaluations, or their ownership
  map.
globs:
  - "commands/**/*.md"
  - "config/governance.json"
  - "evals/**"
  - "rules/**/*.md"
  - "skills/**"
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-08-29","route:project","supersedes:rule:architecture/governance-artifact-composition"]'
---

# Compose governance through one owner per behavior

Classify every surviving statement before editing it:

- a mandatory invariant belongs to one rule;
- a model-selected conditional procedure belongs to one skill;
- an explicitly invoked workflow and its arguments belong to one command;
- deterministic semantic validation belongs to `GovernanceBundle`;
- project discovery, provider adaptation, publication, and generated output belong to AI
  Hub.

Reference the selected owner instead of copying its contract into adjacent artifacts. A
mixed source is split by responsibility; its historical filename, type, wording, or
directory does not survive as an alias.

Skill specialization is a dependency DAG, never copied prose. Universal and project-wide
behavior remains in its general owner; technology/language skills declare only their
delta; framework/library skills declare only the next delta; project-local skills
declare only the final local contract. Every child records `extends:<parent>` and
references `$<parent>` explicitly. Missing parents, cycles, reverse specialization, or
duplicated ancestor rules are invalid.

External and historical artifacts are evidence only. Before adopting behavior, prove its
current requirement and consumer, provenance and license, executable or generated
resources, activation boundary, effects, failure contract, and overlap with canonical
owners. Extend the current owner when it already covers the behavior. A distinct
identity requires an independently recurring outcome and material semantic evaluation.

Reject foreign publishers, fallback, retry, compatibility, partial execution, copied
generated output, private paths, and behavior with no current consumer. After
convergence, update the ownership map, evaluations, inventory, and documentation here;
then AI Hub regenerates every delivery and proves a zero-change second generation.

## Retire a declaration whose subject the governed process consumed

A declaration that describes a population, a remainder, or a pending condition is only
true while its subject exists. When the process it governs consumes that subject — the
population gets adopted, the remainder gets resolved, the condition gets met — the
declaration stops describing anything, and its own gate is what says so first: a count
that must match reads zero because there is nothing left to count.

Retire it at its owner, in the same change that proves the subject is gone. Do not relax
the comparison, widen the bound, or add an exemption to keep a declaration whose
referent no longer exists — that converts a precise gate into a permissive one and hides
the next real divergence behind it.

Retiring means the whole set: the configuration key, its schema type, its validation,
and every implementation only it fed. Prove first that whatever the declaration verified
is still verified by something at least as strong, and name that owner in the change. If
nothing else verifies it, the declaration is still doing work and stays.
