---
description: Apply the mandatory engineering decision and delivery sequence.
capsule_summary: |
  Every implementation: research the owner first, cut scope without a current
  consumer, elect one writable authority and make every other copy a generated
  projection, implement through the owner, remove duplication, then exercise
  runtime behavior and run every applicable gate before changing phase.

  At a cross-boundary failure, prove the producer's contract and fix whichever
  side is wrong — never bend a correct owner for an invalid consumer.

  Hardcodes, normalized failure, failover, retry, fallback, partial execution
  and unevidenced success are defects. The first exception escapes with its
  traceback and cause.
metadata:
  aihub.tags: '["decision:plan-00","effective:2026-08-29","route:both"]'
---

# Engineering core

For every implementation:

1. Research repository owners, dependencies, and canonical documentation.
2. Remove scope without a current requirement or consumer (YAGNI).
3. Elect one writable authority; every other copy is a generated projection
   (SSOT).
4. Apply SOLID only to a responsibility or dependency boundary under change.
5. Implement through the owner and simplify without weakening behavior.
6. Remove duplication and god components; recheck YAGNI, SSOT, SOLID.
7. Exercise runtime behavior, run every applicable native gate, and complete
   the approved landing cycle before changing phase.

At a cross-boundary failure, prove the producer contract and output. Fix its
owner when invalid or the receiver when it conforms. Never alter a correct
adjacent owner for an invalid consumer; symptom workarounds are defects.

Hardcodes, normalized failure, failover, retry, fallback, compatibility,
partial execution, keyring, and unevidenced success are defects. Typed owners
keep defaults. The first exception escapes its CLI with traceback and cause.

Git, runtime, build, and tests are baseline. Every other executable is an
authorized, selected capability; installation or PATH presence never selects
it. Do not load, locate, probe, or gate dormant capabilities. A selected invalid
capability fails without fallback and requires only non-derivable values.

Remote access follows the repository's current Git and forge configuration.
Never rewrite protocols, create identity aliases, or mutate user SSH
configuration as a prerequisite for ordinary Git operations.

An external token validation without its token is not executed and is recorded
as `NOT EXECUTED`, never green; it does not block offline gates, landing, or
post-merge proof. Direct invocation selects it: the token becomes required and
any failure escapes without skip, catch, fallback, or normalization.

Compose with `generalized ownership` (rule file),
`strict execution` (rule file),
`runtime evidence` (rule file),
`storage isolation` (rule file),
`security closure` (rule file).
