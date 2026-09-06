# Security triage contract

This semantic document owns the evidence standard referenced by the governance
map. It is not a scanner runner, tracker, historical ledger, or green-status
record.

Resolve scanner applicability from the managed project's current typed
configuration before invocation. Run the project's root Make security verb only
when selected prerequisites, including required credentials, are present. A
missing prerequisite is `NOT EXECUTED`, never success. Once selected, a nonzero
exit, timeout, signal, incomplete report, or unresolved finding remains red with
its causal output.

Each finding records its scanner identity and version, target revision, command
owner, working directory, exit code, decisive output, severity, technical
decision, correction owner, and independent rerun evidence. Never dismiss,
suppress, downgrade, archive, or convert an execution failure into a finding.
Correct the current owner, rewire every consumer, remove superseded code and
evidence artifacts, and rerun the same Make surface.

This package performs no scans. AI Hub may select and orchestrate scanners for a
managed project, but it cannot report this bundle or an unevaluated credential
state as scanner evidence.
