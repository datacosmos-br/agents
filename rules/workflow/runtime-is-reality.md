---
description: Verify runtime reality before tests or completion claims
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-08-28","route:both"]'
---

# Reality is the running system; tests are checks, not the SSOT

First reproduce and validate the declared public import, API, CLI, daemon, service,
generated consumer, deployed artifact, or other real runtime selected by the project.
Verify its revision or release identity. Only after that contract is measured may tests
be created, adapted, or invoked. An editable checkout, test assertion, snapshot, local
cache, generated copy, or stale environment does not define runtime behavior.

## Causal diagnosis

Every session and project diagnoses before patching. Preserve the exact native failure,
command, working directory, exit, inputs, environment and tool versions,
source/runtime/view identities, original exception and decisive causal observations,
without secrets. Reproduce through the original public entrypoint.
Research the concept in owning source, branch-matched ADRs and SDK/API contracts;
validate external semantics against current official documentation.

Use native debug, diagnostics and tracing to establish the failing mechanism; for
latency, capture representative inputs and profile through the command owner. State
the evidence-supported cause and why the proposed change corrects it before editing.
Distinguish facts from hypotheses and competing explanations. Hypotheses select
investigative observations only, never speculative implementation trials. Instrument
the real path without changing semantics, weakening guards, masking failure or
substituting execution. Missing evidence means continue investigating, not patch-and-see
or phase advancement; neither an unproven claim of certainty nor success alone proves
the cause or validates the concept.

Ground every correction in its applicable canonical rules and verified contract.
Never invent a rule, API, exception, permission or architecture, or depart from an
established rule to make an error disappear. Resolve missing contract evidence at
its owner before changing behavior; an unresolved conflict between current
authorities requires one targeted question before the dependent change.

A request to resolve a failure never authorizes inventing an API, exception or
permission, weakening an established guard, or changing the canonical strategy.
Prove that the correction obeys the existing contract; obtain explicit operator
approval before any actual contract change. Do not use a diagnostic blockage as
permission to bypass that blockage or present its profile as runtime evidence.

Apply the smallest fix at the proven origin, preserving contracts, typed defaults and
references. No fallback, compatibility accommodation, cast or suppression to obtain
green. Re-exercise the original public entrypoint and negative reproduction, then
applicable global gates and persistent incremental tests under
[canonical commands](canonical-commands.md#test-verbs). An independent probe, changed
error or shrinking failure count does not prove the original defect resolved. Bind
   correctness and performance claims to actual source, runtime and captured inputs.
If the original error is unchanged, the defect remains unresolved. Verify with
debugging/tracing that the intended corrected artifact was actually loaded and
locate the failing path before another edit. Never infer success from an applied
patch, or guess a new failure location; a different message alone proves no fix.

Validate each adjustment immediately through that original reproduction before
dependent work or another implementation change. An unchanged original error means
the defect remains unresolved: never call the adjustment a fix or stack another
patch on that claim. Preserve the observed failure, return to diagnosis and tracing,
reassess the causal explanation against the canonical contract, and establish the
next correction before editing again.
Never stack unverified fixes, repeat an unchanged failed attempt, or treat a
different error as success. Full native gates and regressions still remain required;
immediate runtime verification never replaces them.

## The order of work is absolute

This order binds every project, agent, and session without exception (tracker memory
`operator-ruling-2026-10-22-runtime-before-tests`):

1. Make the change work in real execution: the project's real verbs and public entry
   points in the workspace, in standalone members, and in the declared external
   consumers the change reaches.
2. Only then correct warnings, lint, typing, and other static findings.
3. Only then create or adjust tests that lock the observed behavior against regression.

Running a test, a single-file gate, or any static checker to validate a change before
step 1 has produced real-execution evidence is prohibited; a green gate or suite before
that proof is not evidence. Every correction in steps 2 and 3 keeps the real execution
working, and a correction that breaks it is a defect fixed at once, never traded for a
green gate.

This acceptance order does not prohibit an authorized prerequisite repair needed to
restore the real entrypoint while RED, including a causal static or command-owner
defect. Preserve the original failure, repair its origin and re-exercise the runtime;
neither the repair nor an intermediate check admits a phase or proves runtime success.

- A test that only passes by keeping removed or legacy artifacts is wrong: fix or delete
  the test; never restore legacy just to make it pass.
- A config/settings test that breaks when a valid SSOT value changes is defective. Test
  contracts and derivations across arbitrary valid inputs; goldens may lock generated
  structure, never mutable config-owned values.
- A missing facade constant fails only at runtime — import and run the real path.
- Zero executed tests prove no behavioral execution. The integrity-checked incremental
  cache hit allowed by [the test contract](canonical-commands.md#test-verbs) is a cache
  receipt only, with complete deselection accounting, never "tests passed" or fresh
  coverage. Unexplained nonselection, a change with no applicable behavioral proof,
  or `no tests ran` after a collection error remains missing evidence, not green.
- Before concluding root cause, prove the running or installed artifact matches the
  declared authoritative revision or release. An editable checkout, local cache,
  generated copy, or stale environment is not evidence of remote/runtime behavior until
  identity is verified.
- Use the newest released version of every required tool. Every diagnostic it emits is
  blocking. A cap, downgrade, substitution, suppression, compatibility classification,
  or false-positive classification requires prior operator discussion, reproducible
  evidence, and explicit authorization; without all three, correct the owner and rerun
  that released version.
