---
description:
  A production pilot is an acceptance record on the integration branch's integrated
  state, with declared consumer propagation and a real usage cycle.
metadata:
  aihub.tags: '["decision:ADR-0008","effective:2026-09-11","route:both"]'
---

# Pilot homologation and complete propagation law

A "pilot" (homologação) is not a manual npm-script run; it is the coded transition from
an integrated increment to an accepted working state that the product's own declared
verbs can reproduce. It exists only on the integration branch's integrated artifact,
never on a lane checkout or an editable install.

An increment reaches the pilot stage only with every step below proven on the INTEGRATED
state, each with command, cwd, exit code, decisive output, and SHA:

1. **Integration gate**: pull-request review resolved, then a `--no-ff` merge into the
   declared integration branch; every affected native gate re-runs on the merged SHA
   before anything else is declared (compose with
   `rules/workflow/production-readiness.md`).
2. **Propagation to declared consumers**: every consumer project that pins the artifact
   (dependency lock, workspace gitlink, delivered rule layer) re-receives the increment
   through its canonical channel and re-runs its own affected gates on the bumped state.
   Propagation is complete only when the newest consumer generation matches the source
   and its gates are green; a single-consumer proof does not close a multi-consumer
   increment (compose with `rules/workflow/structural-migrations.md` and
   `rules/runtime/deployment-lifecycle.md`).
3. **Runtime acceptance on the installed artifact**: the project's own status or health
   verb exits zero outside the source checkout; editable/source checkouts never stand in
   for runtime evidence.
4. **Real usage cycle**: at least one end-to-end invocation of the product's public
   surface executing the increment's actual behavior, with before/after evidence
   captured; a test-only demonstration is not a usage cycle.
5. **Closure**: the pilot tracker item closes with the four-source proof (registered
   state, integration history, measured reality, current code); loud-opened reds
   captured during the cycle are either fixed with full revalidation or filed as
   blocking child items — never normalized.

Sampling, smoke shortcuts, and "local green" never substitute any step above. A pilot
whose consumer propagation is partial is a staged delivery, not a pilot, and must not be
reported as production-ready.
