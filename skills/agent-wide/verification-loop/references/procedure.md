# Verification loop procedure

Fresh executable evidence bounds a readiness or completion claim. A command
name, stale report, warning, skip, or successful later stage cannot replace a
missing or failed earlier stage.

## Preflight

Before executing a gate or generated-owner effect, resolve and validate:

- the exact changed behavior, paths, consumers, and claim boundary;
- the repository's current authoritative development and public runtime
  commands from its declared owners;
- required environment, toolchain, fixtures, services, and credentials;
- generated surfaces and their canonical owner;
- CI workflows and every changed-path trigger required to select them;
- the ordered gate set required for the affected scope.

Do not invent selectors, options, aliases, private entry points, or direct-tool
substitutes. A missing or conflicting prerequisite stops with zero gate effects.

## Ordered evidence

Run each applicable owner in repository order:

1. environment and bootstrap health;
2. repository check, lint, and formatting owner;
3. static and type analysis owner;
4. complete affected test owner;
5. material use through the shipped public surface;
6. generated-owner convergence and fixed point when generated surfaces changed;
7. native CI on the current published commit, including workflow-source trigger
   coverage when CI configuration changed; and
8. zero-residue and integration evidence at an increment boundary.

The first nonzero exit, timeout, signal, incomplete publication, or missing
decisive output stops the invocation and propagates as the causal result. Do not
catch, retry, switch tools, narrow the gate, continue to later stages, or publish
partial green evidence. Diagnose and correct that root cause at its canonical
owner, then rerun the failed and invalidated stages. This is a new invocation in
the same active phase, not an unchanged retry or a handoff. Ask for help only
when the remaining condition is external or requires authority the active task
does not grant.

Generated effects must stage on the destination filesystem, verify completely,
and publish atomically. Cleanup may attach a secondary failure only while
re-raising the original cause. Leave no generated or temporary residue.

## Report

For every attempted stage record the exact command, working directory, exit
code, decisive output, artifact or runtime observation, timestamp where owned,
and covered scope. Distinguish tests from public-surface proof. State the first
failure and leave later stages unclaimed while fixing it; a report never advances
the phase cursor.

The final claim cannot exceed the common scope of the fresh evidence. Local or
branch-only green cannot be called an implementation completion while required
CI, approval, merge, or post-merge proof remains open. Any later overlapping
edit invalidates earlier evidence without converting it into a warning.
