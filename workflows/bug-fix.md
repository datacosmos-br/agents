# Workflow: bug fix

## Goal

Correct the observed root cause with the smallest complete owner change and a
regression test that proves public behavior.

## Procedure

1. Read repository law, current documentation, owners, consumers, Git state, and
   concurrent WIP.
2. Discover the repository's canonical commands through `make help` or its
   declared equivalent.
3. Reproduce the failure through the real public runtime surface. Record the
   command, cwd, exit code, and decisive output.
4. Trace inputs to the canonical owner. Search all consumers for the same defect
   class before choosing the change.
5. Add or correct an observable regression test. Do not mock away the failing
   boundary or encode an implementation detail.
6. Change the owner and complete the cutover. Remove superseded code, docs,
   fixtures, and compatibility paths in the same change.
7. Re-run the real runtime first, then the affected native lint, format, type,
   test, build, security, and generated-surface gates.
8. Search for contradictory documentation and stale consumers.
9. Follow the landing contract in [WORKFLOWS.md](WORKFLOWS.md).

## Fail-closed rules

- No bypass, fallback, shim, suppression, hardcode, weakened assertion, skipped
  gate, or dual old/new behavior.
- A missing tool, warning, timeout, auth failure, quota failure, or unexplained
  environment difference remains red.
- Preserve unknown and concurrent WIP; never reset, stash, or overwrite it.
- While tracker runtime is suspended, create no substitute tracker or ledger
  and do not call the phase `DONE`.
