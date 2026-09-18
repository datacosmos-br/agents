# Technical writing procedure

## Scope

Use for specifications, ADRs, runbooks, READMEs, API documentation, incident reports,
changelogs, commit messages, and PR descriptions. Do not impose this style on fiction,
poetry, legal text, academic style, or deliberate brand voice.

## Method

1. Identify audience, decision, source facts, required terminology, and length.
2. Lead with the decisive fact, constraint, result, or action. Remove meta introductions
   and ceremonial conclusions.
3. Preserve exact numbers, units, dates, owners, uncertainty, protocol terms, and
   limitations. Never polish an unsupported claim into fact.
4. Use active voice, concrete nouns, short sentences, and sentence-case headings. Prefer
   one precise example over generic adjectives.
5. Delete repetition, hedges, corporate jargon, hype, and sentences that do not change
   understanding or action.
6. Verify commands, links, identifiers, citations, and claims against their sources.
   Mark inference and missing evidence explicitly.

## Commit records

A commit summary names the affected capability and observable change. Its body records
the reason, scope, and decisive validation when known. Derive both from the diff and
integrated state, never from a weak subject alone.

Do not rewrite published history to improve wording. Preserve its SHA and add a factual
interpretation to the current tracker, changelog, release note, ADR, or other canonical
document. Rename an unpublished commit only when authorized and safe for the active
branch.

## Reject

- Stock openings or closings such as “great question”, “let's dive in”, “in conclusion”,
  or “hope this helps”.
- Unsupported superlatives such as “fastest”, “robust”, “seamless”, “innovative”, or
  “game-changing”. Replace them with measured behavior or remove them.
- Empty transitions, repeated sentence shapes, fake quotations, citation placeholders,
  and unexplained acronyms.
- A rewrite that changes policy, technical semantics, attribution, scope, or certainty.

## Evidence record

For an evidence-bearing document, retain the source, measurement context, decisive
values, and limits. If a reader cannot verify a claim, qualify it or remove it.
