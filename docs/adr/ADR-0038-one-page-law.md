# ADR-0038 - One-page law of outcomes

**Status:** Accepted **Date:** 2026-11-03 **Scope:** `rules/law.md`, `AGENTS.md` prelude,
every rule, skill, command and evaluation that restated a law

## Authority

The operator's words are recorded verbatim in the agents tracker memories
`operator-order-2026-11-02-simplicity-rope-ca-di` (the order to rewrite rules, skills,
laws, AGENTS files and memories so that work follows the simplest path, Clean
Architecture with dependency injection, rules at a high level of abstraction and native
tools) and `operator-answers-2026-11-03-one-page-law` (the decisions on the protocol
mirror, the Python rewrite tools, memory pruning, publication, model composition and
layout naming), `operator-answers-2026-11-03-fleet-realignment` (the Gas City deacon,
administrative merge, the dispute rule and routing failover) and
`operator-order-2026-11-03-hooks-binding` (hooks bind every agent and session).

## Context

Measured on 2026-11-02, flext-infra grew from 94,991 lines (2026-08-31) to 266,568
lines, while the universal rules grew from 1,290 to 5,547 lines and the skills from
8,094 to 20,045. 140 flext-infra modules (104,062 lines) keep parsers and rewriters
beside Rope, the native tool that already models the same facts. The governance made
rule text unable to shrink, prescribed mechanisms instead of outcomes, gated deletion
while leaving addition free, and answered each correction with one more clause. Agents
applied it literally, so each correction added code and text and nothing was removed.

## Decision

1. `rules/law.md` is the whole universal law: twelve outcomes on one page. It is the
   only bootstrap rule, and every other rule adds one tool or project fact without
   restating a law.
2. Rules that restated, staged or mechanized a law are merged into it or deleted.
   Coordination facts stay in their few surviving rules and skills, each stated as an
   outcome.
3. Skills and evaluations that gated deletion, demanded proof layers or encoded
   mechanisms are rewritten to the law: the simplify pass applies to every change,
   deleting code without a current consumer needs no extra approval, and a change that
   grows the code is redesigned.
4. Requirements are kept; mechanics are removed. Truth with evidence, preservation of
   the agreed specification, fail loud on one path, zero residue, runtime proof, the
   landing cycle and never destroying another actor's work remain, as outcomes.

## Consequences

The bundle carries one short law and a small set of fact rules. Guarantee names that AI
Hub consumes keep their identities and now resolve to the law or a surviving rule. AI
Hub owns re-projection of the provider homes, which retires the deleted rules' copies.
Project governance (FLEXT `AGENTS.md`, its law skill and ADRs) is rewritten to the same
law in its own repository.
