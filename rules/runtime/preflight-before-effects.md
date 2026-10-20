---
description: Complete bounded-operation validation before externally visible effects
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-10-20","route:both"]'
---

# Preflight the complete bounded operation

Read-only discovery belongs to preflight. Resolve current authority, inputs,
environment, source and destination identities, native capabilities, ownership,
consumer contracts and required authorization through their declared owners.
Do not treat discovery as publication or claim that its success proves the result.

Before the first mutation or externally visible effect of a bounded operation,
validate its complete dependency group and publication conditions. A multi-phase
program proceeds in validated slices; this does not permit publishing part of one
atomic batch while discovering the rest. When prerequisites can change, retain
the canonical ownership/serialization primitive through publication.

## Replacing divergent objects

Inventory every object in the declared replacement scope, including current WIP,
physical identity, provenance, consumers and the proposed owner. Names, age,
location, description or similar shape do not prove semantic equivalence.
Representation-only adoption requires an approved information-preserving typed
transformation and fixed-point proof.

Existing operator authorization may already decide the semantic change and its
disposition. Revalidate it and continue within that scope; do not request the same
approval again merely because old and requested states differ. Fix-forward owns
preservation and integration of current work.

When competing current intentions remain unresolved, or a destructive effect
extends beyond the authorization, stop the affected publication. Present the
exact objects, ownership, semantic delta, blast radius and proposed disposition
as one decision packet. Preserve the current state; do not silently select,
replace or archive it while that decision is open.

## Convergent effects

Distinct required inputs may conclude that the same effect is needed; they do
not justify duplicate implementations of one behavior. Derive a stable identity
key and publish an identical effect once. If payloads differ, apply an already
declared precedence contract at its typed owner. Without that authority, preserve
both facts and ask for the unresolved decision rather than inventing a winner.

Strict execution and atomic-effects rules own failure propagation and transaction
recovery; this rule grants no fallback or partial-success route.
