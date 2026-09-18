---
name: eval-harness
description: "behavioral evaluation, material graders, eval scenarios"
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-08-29","usage:on-demand"]'
---

# Eval Harness

Activate when a behavior, agent, prompt, or workflow needs a repeatable semantic
evaluation. Explaining an assertion or running an owned test does not require a new eval
suite.

## Preflight

Before creating or running an eval, resolve the observable contract, baseline, inputs,
expected material artifact, failure boundary, evaluation owner, and publication
destination. Missing behavior or success criteria stops before any eval artifact is
created; never invent a baseline.

## Minimal suite

- A capability scenario proves the newly required material result.
- A regression scenario proves behavior that must remain unchanged.
- A fail-closed scenario proves the first causal failure and zero effects.
- A should-not-trigger scenario proves absence of activation and of fallback.

Use a deterministic grader whenever the result can be checked by code. Use a model or
human grader only for a stated semantic judgment, with an explicit rubric. Keep
definitions, fixtures, graders, and baselines under the project's declared evaluation
owner; do not create a parallel hierarchy.

## Execution and evidence

Run each required scenario through the repository's evaluation facade. Preserve child
nonzero status, timeout, signal, exception, and causal chain. Do not retry a failed
required trial, substitute another model or grader, or convert failure to a warning,
skip, neutral result, or later success.

`pass@k` measures reliability; it never makes a failed required trial green. `pass^k`
requires every named trial to pass. Publish one complete report only after all required
evidence exists: exact command, exit status, decisive output, artifacts, and each
scenario result.

Remove temporary inputs and superseded reports through the evaluation owner. Completion
requires the material artifact, regression proof, causal failure proof, zero effects,
and no unowned residue.
