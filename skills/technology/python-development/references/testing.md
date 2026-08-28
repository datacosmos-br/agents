# Python testing

## Use the project owner

Discover the repository's public test command and typed selectors before running
tests. Use that surface, normally `make test`, rather than raw pytest flags. The
project owns test targets, timeouts, reports, warnings, coverage, parallelism, and
cache lifecycle.

When the project pins pytest-testmon, keep Testmon as the default impact-analysis
engine. Its database is a persistent acceleration artifact, not a disposable way
to make one invocation green.

## Preserve precise intent and the Testmon database

- An ordinary incremental run uses `--testmon` and may execute only affected or
  previously failing tests.
- An explicit `FILE`, nodeid, or `MATCH` request must execute the complete pytest
  selection while continuing to collect into the existing database. The runner
  uses Testmon's `--testmon-noselect` mode; it does not clear or replace the
  database and does not let impact analysis deselect an explicitly requested
  test.
- A full or CI seed run also uses `--testmon-noselect` when the project uses the
  same database, so the whole selected suite executes and refreshes dependency
  data without a separate destructive rebuild.
- Use `--testmon-forceselect` only through an explicit public mode whose contract
  is the intersection of affected tests and pytest selectors. Never substitute
  that behavior for a request to run one exact test.

Do not delete `.testmondata*`, invoke a rerun-all flag, change the Testmon
environment identity, reinstall the toolchain, or create a parallel cache merely
to run a focused test. Cache maintenance requires the project's declared command
and mutation guard. A genuine Python, package-set, schema, or Testmon-version
incompatibility is reported as invalidation evidence; it is not hidden by an
automatic clear and retry.

## Evidence

For a focused request, require at least one executed test and zero Testmon
deselections inside the explicit selection. A selector matching zero tests stays
nonzero. For a full/seed request, compare the executed count with the collected
scope and require zero impact deselections. Then run an unchanged incremental
invocation and prove that Testmon reuses the same database instead of rebuilding
the whole suite. Warnings, skips, cache resets, and package-change invalidations
remain red unless the project contract explicitly requires and explains them.
